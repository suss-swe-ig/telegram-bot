import urllib3
import tempfile
import requests
import asyncio
import aiohttp

from pathlib import Path
from dotenv import dotenv_values
from datetime import datetime, timedelta

config = dotenv_values(".env")

# tmp directory to store the files
tmpdir = config.get("TMP_DIR", tempfile.gettempdir())

# Function will download the file again if it's more than cache days
# Do not required to download often because course information doesn't change often
cacheDays = config.get("COURSE_INFO_CACHE_DAYS", 30)

# Printing for debugging purpose
# Logging is not required
print('Course info configurations')
print(f'cache_days: {cacheDays}')
print(f'tmpDir: {tmpdir}')

# Try to create tmp directory if provided and does not exists
Path(tmpdir).mkdir(parents=True, exist_ok=True)

# Disable warning on verifying SSL
urllib3.disable_warnings()
async def downloadCourseInfo(courseCode):
    response = { 'statusCode': 200, 'msg': 'OK' }
    if courseCode is None or len(courseCode) == 0:
        # No course code provided
        response['statusCode'] = 400
        response['msg'] = f'No course code is provided'
        return response

    courseCode = courseCode.upper()

    filename = f'{tmpdir}/{courseCode}.pdf'
    path = Path(filename)
    if path.exists():
        fileCreatedTime = datetime.fromtimestamp(path.stat().st_ctime)
        dayDiff = (datetime.today() - fileCreatedTime).days
        if dayDiff < cacheDays:
            print(f'Course info {courseCode} found in cache')
            response['pdf'] = filename
            return response

    url = f'https://sims1.suss.edu.sg/ESERVICE/Public/ViewCourse/ViewCourse.aspx?crsecd={courseCode}&viewtype=pdf&isft=0'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify_ssl=False) as res:
            content = await res.read()

    if res.status != 200:
        # Server unable to return the requested resource
        response['statusCode'] = res.status
        response['msg'] = f'Server unable to provide resource. {courseCode}'
        return response

    if res.headers['Content-Type'] != '.pdf':
        # Resource not found
        response['statusCode'] = 404
        response['msg'] = f'Unable to find course information. {courseCode}'
        return response

    # Success
    with open(filename, 'wb') as outfile:
        outfile.write(content)
        outfile.close()
    response['pdf'] = filename
    return response