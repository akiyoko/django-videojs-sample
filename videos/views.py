from cStringIO import StringIO
import os.path
import re
import time

from boto import connect_s3
from boto.cloudfront import CloudFrontConnection
from boto.cloudfront.distribution import Distribution
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from videos.models import Video

TS_PATTERN = r'^(?!#)\w+\.ts$'


def detail(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        raise Http404("Video does not exist")
    context = {'video': video}
    return render_to_response('videos/detail.html', context)


def get_playlist(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        raise Http404("Video does not exist")

    playlist = get_playlist_with_signed_url(video.playlist_path)
    response = HttpResponse(playlist, content_type="text/plain")
    return response


def get_playlist_with_signed_url(playlist_path):
    # Get playlist file from S3
    s3_conn = connect_s3(settings.ACCESS_KEY_ID, settings.SECRET_ACCESS_KEY)
    bucket = s3_conn.get_bucket(settings.PLAYLIST_BUCKET_NAME)
    key = bucket.get_key(playlist_path)

    if key is None:
        raise Exception("No such key was found. key={}".format(key))

    fp = StringIO()
    key.get_contents_to_file(fp)
    fp.seek(0)

    # Convert with signed url
    cf_conn = CloudFrontConnection(settings.ACCESS_KEY_ID, settings.SECRET_ACCESS_KEY)
    dist = Distribution(cf_conn)
    expire_time = int(time.time() + 60 * 60)  # 60 mins

    outlines = []
    for line in fp.readlines():
        line = line.rstrip()
        matchObj = re.search(TS_PATTERN, line)
        if matchObj is not None:
            file_name = matchObj.group()
            url = os.path.join(os.path.dirname(os.path.join(settings.CLOUDFRONT_URL_PREFIX, playlist_path)), file_name)
            signed_url = dist.create_signed_url(url, settings.CLOUDFRONT_KEYPAIR_ID, expire_time, private_key_file=settings.CLOUDFRONT_PRIVATE_KEY_FILE_LOCATION)
            outlines.append(signed_url)
        else:
            outlines.append(line)
    fp.close()
    return '\n'.join(outlines)
