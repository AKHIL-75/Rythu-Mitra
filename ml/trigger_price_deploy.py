"""Request a Vercel deploy after a validated report has been pushed. No secrets logged."""
import os
from urllib.parse import urlsplit
import requests


def configured_hook():
    value=os.environ.get('VERCEL_DEPLOY_HOOK','').strip()
    try:
        url=urlsplit(value)
        if (url.scheme!='https' or url.hostname!='api.vercel.com' or url.username or url.password
                or url.port not in (None,443) or not url.path.startswith('/v1/integrations/deploy/')
                or len(url.path.rstrip('/').split('/'))!=6 or url.query or url.fragment):
            raise ValueError('Invalid deploy hook')
    except (ValueError,TypeError):
        raise ValueError('Configure VERCEL_DEPLOY_HOOK from your Vercel project Git settings') from None
    return value


def main():
    try:
        hook=configured_hook()
    except ValueError:
        print('Missing or invalid VERCEL_DEPLOY_HOOK. No deploy requested.')
        return 1
    try:
        response=requests.post(hook,timeout=20,allow_redirects=False)
        if not 200<=response.status_code<300:
            print('Vercel deploy hook rejected the request. HTTP:',response.status_code)
            return 1
    except requests.exceptions.RequestException:
        # Exception strings can contain the secret hook URL.
        print('Could not reach the Vercel deploy hook. Check the workflow secret and Vercel status.')
        return 1
    print('Vercel deployment requested. Check the Vercel dashboard for the build result.')
    return 0

if __name__=='__main__':raise SystemExit(main())
