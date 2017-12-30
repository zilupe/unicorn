import os
import requests
import time
from bs4 import BeautifulSoup


from unicorn.configuration import logging


log = logging.getLogger(__name__)


class GmPage:
    def __init__(self, resp):
        log.info('Processing page at {}'.format(resp.url))
        resp.raise_for_status()
        self.text = resp.text
        self.soup = BeautifulSoup(self.text, 'html.parser')

    def get_all_season_links(self, base_url=''):
        for table in self.soup.find_all('table', class_='TFTable'):
            tr_header = table.find('tr', class_='TFHeader')
            if not tr_header:
                continue
            if tr_header.find('td').text.strip() != 'Previous Seasons':
                continue
            for tr in table.find_all('tr', class_='TFRow'):
                td_link = tr.find_all('td')[0]
                yield '{}{}'.format(base_url, td_link.find('a')['href'])

    def get_hidden_input_values(self, form_id=None):
        if form_id:
            all_fields = self.soup.find(id=form_id).find_all('input')
        else:
            all_fields = self.soup.find_all('input')

        for field in all_fields:
            if field['type'] == 'hidden':
                yield field['name'], field['value']


def run():
    gm_username = os.environ['GM_USERNAME']
    gm_password = os.environ['GM_PASSWORD']
    gm_login_url = 'https://gomammoth.spawtz.com/SpawtzApp/Login.aspx'

    session = requests.Session()
    session.headers.update({
        'Referer': 'https://gomammoth.spawtz.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    })

    with session:
        login_page = GmPage(session.get(gm_login_url))
        hidden_inputs = dict(login_page.get_hidden_input_values(form_id='aspnetForm'))
        time.sleep(3)

        login_submission = GmPage(session.post(
            url=gm_login_url,
            data={
                'ctl00$Content$ctl00$txtEmailAddress': gm_username,
                'ctl00$Content$ctl00$txtPassword': gm_password,
                'ctl00$Content$ctl00$chkRememberMe': '',
                'ctl00$Content$ctl00$btnLogin': 'Login',
                **hidden_inputs
            }
        ))
        if 'My Teams (Organisers only)' in login_submission.text:
            log.info('Logged in successfully')
        else:
            log.error('Looks like login failed -- did not find "Logged in successfully" text on page')
        time.sleep(3)

        lost_angels_page = GmPage(session.get('https://gomammoth.spawtz.com/External/Fixtures/TeamProfile.aspx?VenueId=0&TeamId=4896'))
        for link in lost_angels_page.get_all_season_links(base_url='https://gomammoth.spawtz.com/External/Fixtures/'):
            print(link)


if __name__ == '__main__':
    run()
