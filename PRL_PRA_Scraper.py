import re
import requests
import smtplib
import datetime
import poplib

p = poplib.POP3_SSL('pop.gmail.com')
p.user('2.321.drive')
p.pass_('Ry=13.6eV')

mails = [p.retr(emailNum)[1] for emailNum in [int(numstr.split(' ')[0]) for numstr in p.list()[1]]]

p.quit()

addresses_sub = [mail[3].split('<')[1].split('>')[0] for mail in mails if 'subscribe' in mail[34].lower() and 'unsubscribe' not in mail[34].lower()]
addresses_unsub = [mail[3].split('<')[1].split('>')[0] for mail in mails if 'unsubscribe' in mail[34].lower()]

current_file = open('C:/Users/2-321 Desktop/Desktop/Anaconda/subscriberList.txt')
addresses = current_file.read().split('\n')
current_file.close()

for address in addresses_sub:
    if address not in addresses:
        addresses.append(address)
        
for address in addresses_unsub:
    if address in addresses:
        addresses.remove(address)
        
current_file = open('C:/Users/2-321 Desktop/Desktop/Anaconda/subscriberList.txt','w')
current_file.write('\n'.join(addresses))
current_file.close()

current_file = open('C:/Users/2-321 Desktop/Desktop/Anaconda/PRL_PRA_Scraper.txt','r')
current = current_file.read()
current_file.close()
(prl_volume,prl_issue) = re.findall('PRL Volume ([0-9]+), Issue ([0-9]+)',current)[0]
(pra_volume,pra_issue) = re.findall('PRA Volume ([0-9]+), Issue ([0-9]+)',current)[0]

paper_regexp = '<a href="/(.*?[0-9])">(.*?)</a>(?:.*?"authors">)(.*?)</h6>'
sect_regexp_start = '<a name="sect-'
sect_regexp_end = '(?:(?!</section>).)*'
(prl_url,pra_url) = ('http://journals.aps.org/prl/issues/'+prl_volume+'/'+prl_issue,'http://journals.aps.org/pra/issues/'+pra_volume+'/'+pra_issue)
base_url = 'journals.aps.org/'

(prl_req,pra_req) = (requests.get(prl_url),requests.get(pra_url))
(prl_data,pra_data) = (prl_req.text,pra_req.text)

(prl_sect,pra_sect) = (['Letters: Atomic, Molecular, and Optical Physics'],['Rapid Communications: Atomic and Molecular Processes in External Fields, including Interactions with Strong Fields and Short Pulses','Articles: Atomic and Molecular Processes in External Fields, including Interactions with Strong Fields and Short Pulses','Rapid Communications: Quantum Optics, Physics of Lasers, Nonlinear Optics, Classical Optics','Articles: Quantum Optics, Physics of Lasers, Nonlinear Optics, Classical Optics'])
(prl_sect_regexp,pra_sect_regexp) = (['letters-atomic'],['rapid-communications-atomic-and-molecular-p','articles-atomic-and-molecular-p','rapid-communications-quantum-o','articles-quantum-o'])

now = datetime.datetime.now()
msg = 'From: 2-321 Drive\nTo: PRL Email List\nMIME-Version: 1.0\nContent-type: text/html\nSubject: Physical Review Article Update '+str(now.month)+'/'+str(now.day)+'/'+str(now.year)

(new_prl,new_pra) = (not(('<h1>Not Found</h1>' in prl_data)|('Volume '+prl_volume+', Issue '+prl_issue+' (partial)' in prl_data)),not(('<h1>Not Found</h1>' in pra_data)|('Volume '+pra_volume+', Issue '+pra_issue+' (partial)' in pra_data)))

if new_prl:

    msg = msg+'\n\n<font size="3"><u><b>PRL Volume '+prl_volume+', Issue '+prl_issue+':</b></u></font><br><br>'

    for sect,sect_regexp in zip(prl_sect,prl_sect_regexp):
        sect_data = re.findall(sect_regexp_start+sect_regexp+sect_regexp_end,prl_data,re.DOTALL)
        if sect_data:
            prl_papers = re.findall(paper_regexp,sect_data[0])
            msg = msg+'<ul><font size="2"><li><b>'+sect+'</b></li></font></ul>'+'<br>'+'<br><br>'.join(['<a href="'+base_url+paper[0]+'">'+paper[1]+'</a><br>'+paper[2] for paper in prl_papers])
    if msg[-4:]=='<br>':
        msg = msg+'None Found'

    (prl_volume,prl_issue) = (int(prl_volume),int(prl_issue))
    (prl_volume,prl_issue) = (str(prl_volume+(prl_issue==26)),str(prl_issue*(prl_issue<26)+1))

if new_pra:

    if new_prl:
        msg = msg+'<br><br>'
    else:
        msg = msg+'\n\n'
    msg = msg+'<font size="3"><u><b>PRA Volume '+pra_volume+', Issue '+pra_issue+':</b></u></font><br><br>'

    for sect,sect_regexp in zip(pra_sect,pra_sect_regexp):
        sect_data = re.findall(sect_regexp_start+sect_regexp+sect_regexp_end,pra_data,re.DOTALL)
        if sect_data:
            pra_papers = re.findall(paper_regexp,sect_data[0])
            msg = msg+'<ul><font size="2"><li><b>'+sect+'</b></li></font></ul>'+'<br>'+'<br><br>'.join(['<a href="'+base_url+paper[0]+'">'+paper[1]+'</a><br>'+paper[2] for paper in pra_papers])
    if msg[-4:]=='<br>':
        msg = msg+'None Found'

    (pra_volume,pra_issue) = (int(pra_volume),int(pra_issue))
    (pra_volume,pra_issue) = (str(pra_volume+(pra_issue==6)),str(pra_issue*(pra_issue<6)+1))

if any([new_prl,new_pra]):

    msg = msg+'<br><br><br>Send an email to 2.321.drive@gmail.com with the word "unsubscribe" in the body of the email to unsubscribe from this list.'

    s = smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('2.321.drive',password)
    s.sendmail('2.321.drive',addresses,msg.encode('utf8'))
    s.quit()

    current_file = open('C:/Users/2-321 Desktop/Desktop/Anaconda/PRL_PRA_Scraper.txt','w')
    current_file.write('PRL Volume '+prl_volume+', Issue '+prl_issue+'\nPRA Volume '+pra_volume+', Issue '+pra_issue)
    current_file.close()
