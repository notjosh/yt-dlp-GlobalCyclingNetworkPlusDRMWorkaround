import json

from yt_dlp.networking.exceptions import HTTPError
from yt_dlp.utils import (
    determine_ext,
    ExtractorError,
    float_or_none,
    int_or_none,
    strip_or_none,
    unified_timestamp,
)

from yt_dlp.extractor.dplay import GlobalCyclingNetworkPlusIE

class GlobalCyclingNetworkPlusDRMWorkaroundIE(GlobalCyclingNetworkPlusIE, plugin_name='GlobalCyclingNetworkPlusDRMWorkaround'):
    def _download_video_playback_info(self, disco_base, video_id, headers):
        if not self._configuration_arg('use_drm_workaround'):
            return super()._download_video_playback_info(disco_base, video_id, headers)

        return self._download_json(
            disco_base + 'playback/v3/videoPlaybackInfo',
            video_id, headers=headers, data=json.dumps({
                'deviceInfo': {
                    'adBlocker': False,
                },
                'videoId': video_id,
                # 'wisteriaProperties': {
                #     'platform': 'desktop',
                #     'product': self._PRODUCT,
                # },
            }).encode('utf-8'))['data']['attributes']['streaming']

    def _get_disco_api_info(self, url, display_id, disco_host, realm, country, domain=''):
        if not self._configuration_arg('use_gcn_metadata'):
            return super()._get_disco_api_info(url, display_id, disco_host, realm, country, domain)

        country = self.get_param('geo_bypass_country') or country
        geo_countries = [country.upper()]
        self._initialize_geo_bypass({
            'countries': geo_countries,
        })
        disco_base = 'https://%s/' % disco_host
        headers = {
            'Referer': url,
        }
        self._update_disco_api_headers(headers, disco_base, display_id, realm)
        try:
            video = self._download_json(
                disco_base + 'content/videos/' + display_id, display_id,
                headers=headers, query={
                    'fields[channel]': 'name',
                    'fields[image]': 'height,src,width',
                    'fields[show]': 'name',
                    # 'fields[tag]': 'name',
                    # 'fields[video]': 'description,episodeNumber,name,publishStart,seasonNumber,videoDuration',
                    # 'include': 'images,primaryChannel,show,tags'
                    'include': 'images,primaryChannel,show,tags,taxonomyNodes'
                })
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status == 400:
                self._process_errors(e, geo_countries)
            raise
        video_id = video['data']['id']
        info = video['data']['attributes']
        title = info['name'].strip()
        formats = []
        subtitles = {}
        try:
            streaming = self._download_video_playback_info(
                disco_base, video_id, headers)
        except ExtractorError as e:
            if isinstance(e.cause, HTTPError) and e.cause.status == 403:
                self._process_errors(e, geo_countries)
            raise
        for format_dict in streaming:
            if not isinstance(format_dict, dict):
                continue
            format_url = format_dict.get('url')
            if not format_url:
                continue
            format_id = format_dict.get('type')
            ext = determine_ext(format_url)
            if format_id == 'dash' or ext == 'mpd':
                dash_fmts, dash_subs = self._extract_mpd_formats_and_subtitles(
                    format_url, display_id, mpd_id='dash', fatal=False)
                formats.extend(dash_fmts)
                subtitles = self._merge_subtitles(subtitles, dash_subs)
            elif format_id == 'hls' or ext == 'm3u8':
                m3u8_fmts, m3u8_subs = self._extract_m3u8_formats_and_subtitles(
                    format_url, display_id, 'mp4',
                    entry_protocol='m3u8_native', m3u8_id='hls',
                    fatal=False)
                formats.extend(m3u8_fmts)
                subtitles = self._merge_subtitles(subtitles, m3u8_subs)
            else:
                formats.append({
                    'url': format_url,
                    'format_id': format_id,
                })

        creator = series = None
        tags = []
        thumbnails = []
        gcnplustypes = []
        sports = []
        included = video.get('included') or []
        if isinstance(included, list):
            for e in included:
                attributes = e.get('attributes')
                if not attributes:
                    continue
                e_type = e.get('type')
                if e_type == 'channel':
                    creator = attributes.get('name')
                elif e_type == 'image':
                    src = attributes.get('src')
                    if src:
                        thumbnails.append({
                            'url': src,
                            'width': int_or_none(attributes.get('width')),
                            'height': int_or_none(attributes.get('height')),
                        })
                elif e_type == 'show':
                    series = attributes.get('name')
                elif e_type == 'tag':
                    name = attributes.get('name')
                    if name:
                        tags.append(name)
                elif e_type == 'taxonomyNode' and attributes.get('kind') == 'gcnplustype':
                    name = attributes.get('name')
                    if name:
                        gcnplustypes.append(name)
                elif e_type == 'taxonomyNode' and attributes.get('kind') == 'sport':
                    name = attributes.get('name')
                    if name:
                        sports.append(name)
        
        summary = strip_or_none(info.get('description'))
        description = strip_or_none(info.get('longDescription'))

        if not description:
            description = summary
            summary = None

        return {
            'id': video_id,
            'display_id': strip_or_none(info.get('alternateId'), display_id),
            'title': title,
            'description': description,
            'summary': summary,
            'duration': float_or_none(info.get('videoDuration'), 1000),
            'timestamp': unified_timestamp(info.get('publishStart')),
            'series': series,
            'season_number': int_or_none(info.get('seasonNumber')),
            'episode_number': int_or_none(info.get('episodeNumber')),
            'creator': creator,
            # 'tags': tags,
            'categories': sports,
            'tags': gcnplustypes,
            'thumbnails': thumbnails,
            'formats': formats,
            'subtitles': subtitles,
            'http_headers': {
                'referer': domain,
            },
        }