import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// x264 gives broad compatibility; the bundled ffmpeg handles the encode.
Config.setCodec('h264');
