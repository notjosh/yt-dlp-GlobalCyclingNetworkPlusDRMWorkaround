import json

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