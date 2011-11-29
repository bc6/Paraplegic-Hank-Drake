from service import Service, SERVICE_STOPPED, SERVICE_START_PENDING, SERVICE_RUNNING
import blue
import uthread
import sys
import random
import log
import smtplib
from email.Header import Header
from email.mime import multipart, text, base
LOCATION_TQ = 1
LOCATION_BFC = 2
LOCATION_CCP = 3
LOCATION_OTHER = 4
LOCATION_CHAOS = 5

class EmailSvc(Service):
    __guid__ = 'svc.emailSvc'
    __displayname__ = 'Email Service'

    def __init__(self):
        self.smptRetryTime = 12000
        Service.__init__(self)



    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.computername = blue.pyos.GetEnv().get('COMPUTERNAME', '?')
        self.domain = blue.pyos.GetEnv().get('USERDOMAIN', '?')
        self.mail_queue = uthread.Queue()
        self.mail_server = None
        uthread.new(self._EmailSvc__mailqueue)
        self.state = SERVICE_RUNNING



    def Stop(self, memStream = None):
        self.state = SERVICE_STOPPED



    def GetMailServer(self):
        if not self.mail_server:
            try:
                local_hostname = blue.pyos.GetEnv().get('COMPUTERNAME', '?')
                self.mail_server = None
                server = self.AppGetMailServer()
                if server:
                    server = server.split(';')
                    if type(server) != type([]):
                        server = [server]
                    server = random.choice(server).encode('latin1')
                    self.LogInfo('Email service using server:', server)
                    if sys.version_info[:3] == (2, 2, 1):
                        self.mail_server = smtplib.SMTP(server)
                    else:
                        self.mail_server = smtplib.SMTP(server, local_hostname=local_hostname)
            except StandardError:
                self.LogError('Mail server bombed')
                log.LogException()
                sys.exc_clear()
                self.mail_server = None
        return self.mail_server



    def AppGetMailServer(self):
        self.LogError('AppGetMailServer not overridden!')



    def SendMail(self, *args, **kw):
        self.mail_queue.put((args, kw))



    def __mailqueue(self):
        self.LogInfo('Email service:  Starting Mail Queue thread')
        try:
            while self.state != SERVICE_STOPPED:
                try:
                    (args, kw,) = self.mail_queue.get()
                    self.LogInfo('Email service:  Got mail from Mail Queue')
                    srv = self.GetMailServer()
                    if srv:
                        self.LogInfo('Email service:  Sending mail')
                        srv.sendmail(*args, **kw)
                        self.LogInfo('Email sercice:  Mail sent')
                    else:
                        self.LogWarn('Email service:  No mail server available, mail not sent.  sendmail args=', args, 'kw=', kw)
                except smtplib.SMTPServerDisconnected:
                    self.mail_server = None
                    self.mail_queue.put((args, kw))
                    self.LogWarn('Failed to send alert, SMTP server disconnected. Will try again in 1 minute')
                    sys.exc_clear()
                    blue.pyos.synchro.SleepWallclock(60000)
                except smtplib.SMTPRecipientsRefused as e:
                    self.LogMailSendFailure('SMTPRecipientsRefused', args, e)
                except smtplib.SMTPSenderRefused as e:
                    self.LogMailSendFailure('SMTPSenderRefused', args, e)
                except Exception:
                    self.LogError('Email service:  Unexpected error during mailqueue processing')
                    log.LogException()
                    self.mail_server = None
                    blue.pyos.synchro.SleepWallclock(60000)


        finally:
            self.LogInfo('Email service:  Stopping Mail Queue thread')




    def LogMailSendFailure(self, failureStr, args, excpt):
        try:
            subject = ''
            lines = args[2].split('\n')
            for each in lines:
                if each.lower().find('subject:') == 0:
                    subject = each

            self.LogError('Email service:  Message in mail queue not allowed to relay, removing message:', failureStr, 'Server:', self.AppGetMailServer(), 'To:', args[1], subject, excpt)
        except:
            self.LogError('Email service:  Message in mail queue not allowed to relay, removing message:', failureStr, 'Server:', self.AppGetMailServer() or '*** unknown server ***', excpt)
            sys.exc_clear()




class NewEmail:
    __guid__ = 'mail.new'

    def __init__(self):
        self.mailfrom = ''
        self.rcptto = ''
        self.cc = ''
        self.bcc = ''
        self.subject = ''
        self.body = ''
        self.html = 0
        self.fileAttachments = []
        self.extraHeaders = {}
        self.rcpt = []
        self.msg = multipart.MIMEMultipart()



    def AttachFile(self, fileName, data):
        self.fileAttachments.append([fileName, data])



    def AddHeader(self, k, v):
        self.extraHeaders[k] = v



    def AddSubject(self, s):
        self.subject += s



    def AddBody(self, b):
        self.body += b



    def CreateMail(self):
        if type(self.subject) == type(u''):
            self.subject = str(Header(unicode(self.subject), 'ISO-8859-1'))
        else:
            self.subject = str(self.subject)
        self.msg['Subject'] = self.subject
        self.rcpt = []
        if self.mailfrom != '':
            self.msg['From'] = str(self.mailfrom)
        if self.rcptto != '':
            self.msg['To'] = str(self.rcptto)
            self.rcpt += str(self.rcptto).split(';')
        if self.cc != '':
            self.rcpt += str(self.cc).split(';')
            self.msg['Cc'] = self.cc
        if self.bcc != '':
            self.rcpt += str(self.bcc).split(';')
        for (k, v,) in self.extraHeaders.items():
            self.msg[k] = v

        charset = 'iso-8859-1'
        subtype = 'plain'
        body = self.body
        if type(body) is unicode:
            body = body.encode('utf-8')
            charset = 'utf-8'
        if self.html:
            subtype = 'html'
        body = text.MIMEText(body, _subtype=subtype, _charset=charset)
        self.msg.attach(body)
        for (fileName, data,) in self.fileAttachments:
            (mimetype, encoding,) = mimetypes.guess_type(filename, 0)
            (maintype, subtype,) = mimetype.split('/', 1)
            attach = mime.base.BASEMime(maintype, subtype)
            attach.set_payload(data)
            encoders.encode_base64(attach)
            attach.add_header('Content-Disposition:', 'attachment; filename="%s"' % str(fileName))
            self.msg.attach(attach)

        return self.msg.as_string()



    def Send(self):
        mime = self.CreateMail()
        sm.StartServiceAndWaitForRunningState('emailSvc').SendMail(self.mailfrom, self.rcpt, mime)




