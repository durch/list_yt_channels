# coding=utf-8

import urllib
import json
import sys
import logging

import click
import requests
import arrow
import attr


def get_video_url(video_id):
    ret_val = f'https://www.youtube.com/watch?v={video_id}'
    logger.debug('Video URL: %s', ret_val)
    return ret_val


logging.basicConfig(format='%(levelname) -10s %(asctime)s %(module)s at line %(lineno)d: %(message)s')
logger = logging.getLogger('ytvideosfinder')


@attr.s
class YtLister(object):
    channel_id = attr.ib()
    api_key = attr.ib()
    published_after = attr.ib()
    published_before = attr.ib()
    base_url = 'https://www.googleapis.com/youtube/v3'
    max_results = 50

    def search_url(self):
        return f'{self.base_url}/search'

    def channels_url(self):
        return f'{self.base_url}/channels'

    def get_channel_videos_in_interval(self):
        logger.info('Getting videos published before %s and after %s', self.published_after, self.published_before)
        ret_val = []
        found_all = False
        next_page_token = ''

        while not found_all:

            params = {
                "key": self.api_key,
                "channelId": self.channel_id,
                "part": "id",
                "order": "date",
                "publishedBefore": self.published_before,
                "publishedAfter": self.published_after,
                "pageToken": next_page_token,
                "maxResults": self.max_results
            }

            encoded_params = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})

            url = f"{self.search_url()}?{encoded_params}"
            logger.info('Request: %s', url)

            logger.debug('Sending request')
            response = requests.get(url)

            logger.debug('Parsing the response')
            response_as_json = response.json()

            returned_videos = response_as_json['items']
            logger.debug('Response: %s', json.dumps(returned_videos, indent=4))

            for video in returned_videos:
                ret_val.append(video)

            try:
                next_page_token = response_as_json['nextPageToken']
                logger.info('More videos to load, continuing')
            except KeyError:
                logger.info('No more videos to load')
                found_all = True
        logger.info('Found %d video(s) in this time interval', len(ret_val))
        return ret_val

    def get_channel_videos(self):

        logger.info('Searching for videos published in channel between %s and %s', self.published_after,
                    self.published_before)
        if self.published_after is not None and self.published_before is not None:
            if self.published_before < self.published_after:
                raise Exception('The date to start from cannot be before the date to go back to!')

        ret_val = self.get_channel_videos_in_interval()

        logger.info('Found %d video(s) in total', len(ret_val))
        return ret_val


@click.command()
@click.option("--api-key", "-k", required=True,
              help='Google Data API key to use. You can get one here: https://console.developers.google.com')
@click.option('-c', '--channel_id', help='Youtube channel to get videos from', required=True)
@click.option('-o', '--output-file-path', default=None,
              help='File to write found video links to (content replaced each time)')
@click.option('-f', '--published-after', default=None,
              help='Only list videos published after this date, otherwise list all')
@click.option('-t', '--published-before', default=None,
              help='Only list videos published before this date, otherwise list all')
@click.option('-v', '--verbose', count=True, help="Verbosity level, WARN, INFO, DEBUG")
def cli(**kwargs):
    # channel_id = getChannelId(args.channel, args.apiKey)

    yt = YtLister(
        kwargs["channel_id"],
        kwargs["api_key"],
        None or arrow.get(kwargs['published_after'] or arrow.utcnow().shift(months=-1).format()),
        None or arrow.get(kwargs['published_before']),
    )

    logger.info('Date to start from: %s', yt.published_after)
    logger.info('Date to go back to: %s', yt.published_before)

    # if interval is not None:
    #     time_interval = datetime.timedelta(days=int(interval))
    # else:
    #     time_interval = datetime.timedelta(weeks=4)

    verbose = kwargs['verbose']
    if verbose == 1:
        logger.setLevel(logging.WARNING)
    elif verbose == 2:
        logger.setLevel(logging.INFO)
    elif verbose >= 3:
        logger.setLevel(logging.DEBUG)

    channel_videos = yt.get_channel_videos()

    if not len(channel_videos) > 0:
        logger.info("No video found for channel!")
        sys.exit(0)

    logger.info('Generating links for found videos')
    video_urls = []
    for video in channel_videos:
        logger.debug('Processing video: %s', json.dumps(video, indent=4))
        video_id = video.get('id').get('videoId')
        if video_id is None:
            logger.info(f"This is probabl a playlist: {video}")
        else:
            logger.debug('Video id: %s', video_id)
            video_urls.append(get_video_url(video_id))
    output_file_path = kwargs['output_file_path']
    if output_file_path is not None:
        logger.debug('File output enabled')
        logger.info('Links will be written to %s', kwargs["output_file_path"])

        with open(output_file_path, 'w') as fp:
            for video_url in video_urls:
                fp.write(video_url + "\n")
    else:
        for video_url in video_urls:
            print(video_url)
    logger.info('Done!')


if __name__ == "__main__":
    cli()
