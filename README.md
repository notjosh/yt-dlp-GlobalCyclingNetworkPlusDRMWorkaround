This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme) to work around GCN content protected by DRM.

By default, this plugin won't do anything. Using the `use_drm_workaround` argument will activate it:

```sh
yt-dlp --extractor-args 'globalcyclingnetworkplus:use_drm_workaround' https://plus.globalcyclingnetwork.com/watch/...
```

Note: this plugin doesn't actually circumvent DRM (i.e. via decrypting protected content), but simply requests content that isn't protected by DRM (as my browser happens to do by default).

More specifically, the backend serves content with `h264-dash-fmp4-fhd-sdr-widevine-cenc` profile (i.e. with DRM) in some circumstances and `h264-hls-ts-fhd-sdr-free-clear` (i.e. without DRM) in others.

I don't know if it's a mistake, or how long it'll last, but enjoy it while you can!

## Installation

Requires yt-dlp `2023.01.02` or above.

You can install this package with pip:

```
python3 -m pip install -U https://github.com/notjosh/yt-dlp-GlobalCyclingNetworkPlusDRMWorkaround/archive/master.zip
```

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.

## Development

See the [Plugin Development](https://github.com/yt-dlp/yt-dlp/wiki/Plugin-Development) section of the yt-dlp wiki.
