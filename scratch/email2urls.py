import email
import imaplib
import pocket
import re
import time
import operator

print('preparing API access...')
p = pocket.Pocket(
        consumer_key='...',
        access_token='...',
    )

def find_urls(data):
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return set(re.findall(url_regex, data))

def download(offset=0, count=10):
    print('downloading known urls...')
    tmp = p.retrieve()['list']
    known = set(map(operator.itemgetter('given_url'), tmp.values()))
    print(f'got {len(known)} known urls')
    known |= set(map(lambda x: x.get('resolved_url', ''), tmp.values()))
    print(f'got {len(known)} known urls')

    for x in list(sorted(known))[:10]:
        print(x)

    urls = set()
    with imaplib.IMAP4_SSL('mail.runbox.com') as imap:
        print('logging into email...')
        imap.login('...', '...')
        print(imap.list())
        rv, data = imap.select('Archive.Notes')
        assert rv == 'OK'
        rv, data = imap.search(None, "ALL")
        assert rv == 'OK'

        email_ids = data[0].split()
        for i, num in enumerate(email_ids):
            if i < offset:
                continue
            if i > offset + count:
                break
            rv, data = imap.fetch(num, '(RFC822)')
            if rv != 'OK':
                print("ERROR getting message", num)

            msg = email.message_from_bytes(data[0][1])
            for part in msg.walk():
                for url in find_urls(part.as_string()):
                    if '</a></p>' in url:
                        url = url.replace('</a></p>', '')
                        url = url.replace('</a>', '')
                        url = url.replace('&amp;', '&')
                        urls.add(url)

            urls -= known

            print(f'processed {i}/{len(email_ids)} emails, {len(urls)} urls to add.')

            if len(urls) > 200:
                print('adding urls to pocket...')
                for url in urls:
                    p.bulk_add(None, url=url)
                p.commit()
                p.reset()
                known |= urls
                urls = set()
                time.sleep(5)

    for url in urls:
        p.bulk_add(None, url=url)
        p.commit()
        p.reset()

