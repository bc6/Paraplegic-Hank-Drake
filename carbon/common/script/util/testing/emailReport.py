import blue
import util
import sys
import re
import __builtin__
import os
from itertools import imap, ifilter
ORCHESTRATOR_REPORTS_PATH = 'reports'
ORCHESTRATOR_REPORTS_FILENAME_PREFIX = 'orchestratorReport'

def SendSummaryMail(testResults, replyToAddress = 'orchestrator@ccpgames.com', sender = None, recipients = None, html = True, sendIfFailOnly = False, timeTaken = None, fileAttachments = [], logToDatabaseResults = {}):
    numTests = len(testResults)
    numTestsFailed = 0
    for testResult in testResults.itervalues():
        if not testResult.wasSuccessful():
            numTestsFailed += 1
        elif testResult.previousRunResult != 'P':
            if getattr(__builtin__, 'ONLYEMAILRESULTMAILLIST', False) is False:
                for (testCase, errorMessage,) in testResult.errors:
                    recipients.append(testCase.GetOwners())

                for (testCase, errorMessage,) in testResult.failures:
                    recipients.append(testCase.GetOwners())


    computerName = blue.pyos.GetEnv().get('COMPUTERNAME', '?')
    if numTestsFailed > 0:
        highImportance = True
        sender = sender or 'Orchestrator FAILURE on %s <%s>' % (computerName, replyToAddress)
    else:
        highImportance = False
        sender = sender or 'Orchestrator Master on %s <%s>' % (computerName, replyToAddress)
    recipients = recipients or ['mnichols@ccpgames.com']
    if sendIfFailOnly and not numTestsFailed:
        return 
    if getattr(__builtin__, 'CURRENTTESTINGREVISION', None) is not None:
        revisionNumber = int(__builtin__.CURRENTTESTINGREVISION)
    else:
        revisionNumber = boot.build
    subject = _BuildEmailSubject(numTestsFailed, revisionNumber, computerName)
    message = _BuildEmailMessage(numTestsFailed, testResults, revisionNumber, timeTaken, logToDatabaseResults)
    if getattr(__builtin__, 'SAVEEMAILTOFILE', None) is True:
        _WriteSummaryToFile(message, revisionNumber)
    _SendMail(subject, message, sender, recipients, html, fileAttachments, highImportance)



def _WriteSummaryToFile(summaryToWrite, revisionNumber):
    if not os.path.exists(ORCHESTRATOR_REPORTS_PATH):
        os.mkdir(ORCHESTRATOR_REPORTS_PATH)
    reportFile = os.path.join(ORCHESTRATOR_REPORTS_PATH, ORCHESTRATOR_REPORTS_FILENAME_PREFIX + str(revisionNumber) + '.htm')
    emailFile = open(reportFile, 'w')
    emailFile.writelines(summaryToWrite)
    emailFile.close()



def _BuildEmailSubject(numTestsFailed, revisionNumber, computerName):
    subject = computerName
    if numTestsFailed:
        subject += ' FAILURE'
    else:
        subject += ' PASSED'
    subject = subject + ' Revision: %s' % str(revisionNumber)
    return subject



def _BuildEmailMessage(numTestsFailed, testResults, revisionNumber, timeTaken, logToDatabaseResults = {}):
    message = _CreateOpeningHTML()
    if numTestsFailed:
        (headerText, headerSubtext,) = ('TEST FAILURE', 'Details:')
    else:
        (headerText, headerSubtext,) = ('All tests PASSED', 'No failures detected')
    if timeTaken:
        message += '<p>Time taken to run tests: %s<br></p>' % str(util.FmtTimeInterval(timeTaken))
    numErrored = 0
    numFailed = 0
    numSkipped = 0
    for result in testResults.itervalues():
        if result.errors:
            numErrored += 1
        elif result.failures:
            numFailed += 1
        elif result.skipped:
            numSkipped += 1

    numPassed = len(testResults) - numErrored - numFailed - numSkipped
    message += 'Ran %d tests. %d passed. %d skipped. %d failed. %d errored<br>' % (len(testResults),
     numPassed,
     numSkipped,
     numFailed,
     numErrored)
    computerName = blue.pyos.GetEnv().get('COMPUTERNAME', '?')
    message += 'Test logs are available at \\\\%s\\logs and crash dumps at \\\\%s\\CrashDumps<br>' % (computerName.upper(), computerName.upper())
    loggingToDatabaseFailed = any(imap(lambda x: x is not None, logToDatabaseResults.itervalues()))
    if loggingToDatabaseFailed:
        message += 'Some tests failed to add their information to the database<br>'
    message += '\n    <h3 align="left"><font face="Arial" size="4">%s</font></h3>\n    ' % headerText
    lastTestSuite = ''
    suiteTableOpen = False
    testNames = testResults.keys()
    testNames.sort()
    nonGatingFailures = 0
    if numTestsFailed != 0:
        message += '<h3><font face=Arial>Failed Tests:</font></h3>'
        skipBR = True
        for testName in testNames:
            testResult = testResults[testName]
            if not testResult.wasSuccessful():
                if not skipBR:
                    message += '<br>'
                else:
                    skipBR = False
                if getattr(testResult, '__NONGATING__', False) is True:
                    testName = testName + '*'
                    nonGatingFailures = nonGatingFailures + 1
                message += '<font face=Arial>' + testName + '</font>'

        if nonGatingFailures > 0:
            message += "<br>* This test marked as 'non-gating' indicating this failure will not prevent code distribution<br>"
    message += '\n    <h3><font face=Arial>%s</font></h3>\n    <p align="left">\n    <table cellspacing="0" cellpadding="3" width="100%%" align="center" border="0">\n    <tr>\n    ' % headerSubtext
    for testName in testNames:
        testResult = testResults[testName]
        if testResult.errors or testResult.failures:
            testSuiteName = testName.split('.')[0]
            if lastTestSuite != testSuiteName:
                if suiteTableOpen:
                    message += _CreateTestSuiteTableClosingHTML()
                message += _CreateTestSuiteTableOpeningHTML(testSuiteName)
                suiteTableOpen = True
            trace = ''
            testowners = []
            if testResult.errors:
                result = 'ERROR'
                for (testCase, errorMessage,) in testResult.errors:
                    trace += errorMessage.replace('<', '&lt;').replace('>', '&gt;') + '\n\n'
                    testOwners = testCase.GetOwners()

            else:
                result = 'FAILED'
                for (testCase, errorMessage,) in testResult.failures:
                    trace += errorMessage.replace('<', '&lt;').replace('>', '&gt;') + '\n\n'
                    testOwners = testCase.GetOwners()

            message += _CreateTestCaseTableLabelHTML(testName)
            message += _CreateTestCaseTableHTML(testName, revisionNumber, result, trace, testOwners, testResult)
            lastTestSuite = testSuiteName

    if suiteTableOpen:
        message += _CreateTestSuiteTableClosingHTML()
    message += '</table>'
    if numSkipped > 0:
        message += '<br><br><h3><font face=Arial>Skipped Tests:</font></h3>'
        for testName in testNames:
            testResult = testResults[testName]
            if testResult.skipped:
                message += '<br><font face=Arial>' + testName + ': ' + testResult.skipped[0][1] + '</font>'

    if numTestsFailed + numSkipped != len(testResults):
        message += '<br><br><h3><font face=Arial>Passed Tests:</font></h3>'
        message += '<table bordercolor="#0" cellspacing="0" cellpadding="3" width="100%%" align="center" border="1" bgcolor="#f5f5f5"><tr><td><font face=Arial>Test Name</font></td><td><font face=Arial>Last Failure</font></td></tr>'
        for testName in testNames:
            testResult = testResults[testName]
            if testResult.wasSuccessful() and len(testResult.skipped) == 0:
                lastFailString = _CreateLastPassFailString(testResult.previousFailureDate, testResult.previousFailureChangelist, testResult.previousFailureCount)
                message += '<tr><td><font face=Arial>' + testName + '</font></td><td><font face=Arial>' + lastFailString + '</font></td></tr>'

        message += '</table>'
    if loggingToDatabaseFailed:
        message += '<br><br><h3><font face=Arial>Database Errors:</font></h3>'
        for (key, value,) in ifilter(lambda pair: pair[1] is not None, logToDatabaseResults.iteritems()):
            message += '<br><font face=Arial>%s</font> failed to log to the database with error %s' % (key, value.replace('\n', '<br>').replace('\t', '&nbsp;' * 4))

    message += _CreateClosingHTML()
    return message



def FormatBlock(block):
    lines = str(block).split('\n')
    while lines and not lines[0]:
        del lines[0]

    while lines and not lines[-1]:
        del lines[-1]

    ws = re.match('\\s*', lines[0]).group(0)
    if ws:
        lines = map(lambda x: x.replace(ws, '', 1), lines)
    while lines and not lines[0]:
        del lines[0]

    while lines and not lines[-1]:
        del lines[-1]

    return '\n'.join(lines) + '\n'



def _CreateOpeningHTML():
    return FormatBlock('\n        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">\n        <html>\n        <head>\n        <meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1" >\n        <title>System Test Summary Email</title>\n        </head>\n        <body bgcolor="#ffffff">\n       \n    ')



def _CreateClosingHTML():
    return FormatBlock('\n        </p>\n        </body>\n        </html>\n    ')



def _CreateTestSuiteTableOpeningHTML(suiteName):
    return FormatBlock('\n      <tr>\n        <td>\n          <p align="left">\n          <table cellspacing="0" cellpadding="10" width="800" align="left" border="0" bgcolor="#eeeeca">\n            <tr>\n              <td>\n                <table cellspacing="0" cellpadding="3" width="800" align="center" border="0" bgcolor="#ffffea">\n                  <tr>\n                    <td>\n                      <p><font face="Arial"><b>%s</b><br></font>\n                      <table bordercolor="#0" cellspacing="0" cellpadding="3" width="100%%" align="center" border="1" bgcolor="#f5f5f5">\n    ' % suiteName)



def _CreateTestSuiteTableClosingHTML():
    return FormatBlock('\n          </tr></table></p></td></tr></table>\n        </td></tr></table></p></td></tr>\n    ')



def _CreateTestCaseTableLabelHTML(testName):
    return FormatBlock('\n      <tr>\n        <td nowrap><font face="Arial">Test Name</font></td>\n        <td nowrap><font face="Arial"><b>%s</b></font></td>\n        <td nowrap><font face="Arial">Trace</font></td></tr>\n    ' % (testName,))



def _CreateLastPassFailString(date, changelist, count):
    if date is None:
        resultString = 'Not in recent history'
    else:
        resultString = str(date) + ' - cl# ' + str(changelist) + '<br>' + str(count) + ' runs ago'
    return resultString



def _CreateTestCaseTableHTML(testName, lastRevision, result, trace, testOwners, testResultObject):
    testOwnersHTML = ''
    for emailAddy in testOwners:
        testOwnersHTML += '<a href="mailto:' + str(emailAddy) + '">' + str(emailAddy) + '</a>; '

    testOwnersHTML = testOwnersHTML.rstrip('; ')
    lastPassString = _CreateLastPassFailString(testResultObject.previousPassDate, testResultObject.previousPassChangelist, testResultObject.previousPassCount)
    lastFailString = _CreateLastPassFailString(testResultObject.previousFailureDate, testResultObject.previousFailureChangelist, testResultObject.previousFailureCount)
    return FormatBlock('\n          <tr><td><font face="Arial">Changelist</font></td><td><font face="Arial">%d</font></td><td rowspan="5">%s</td></tr>\n          <tr><td><font face="Arial">Result</font></td><td><font face="Arial">%s</font></td></tr>\n          <tr><td nowrap><font face="Arial">Last Pass</font></td><td><font face="Arial">%s</font></td></tr>\n          <tr><td nowrap><font face="Arial">Last Fail</font></td><td><font face="Arial">%s</font></td></tr>\n          <tr><td><font face="Arial">Owners</font></td><td><font face="Arial">%s</font></td></tr>\n    ' % (lastRevision,
     _FormatStrForHTML(trace),
     result,
     lastPassString,
     lastFailString,
     testOwnersHTML))



def _FormatStrForHTML(string):
    string = string.replace('\n', '<br>')
    string = string.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    string = string.replace('  ', '&nbsp;&nbsp;')
    return string



def _SendMail(subject, message, sender, recipients, html, fileAttachments, highImportance = False):
    from email.MIMEText import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMENonMultipart import MIMENonMultipart
    from email.MIMEBase import MIMEBase
    from email import Encoders
    msg = MIMEMultipart()
    if html:
        subtype = 'html'
        charset = 'iso8859'
    else:
        subtype = 'plain'
        charset = 'us-ascii'
    if type(message) is unicode:
        message = message.encode('utf-8')
        charset = 'utf-8'
    att = MIMEText(message, subtype, charset)
    msg.attach(att)
    subject = subject.replace('\n', '').replace('\r', '')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    if highImportance:
        msg['X-MSMail-Priority'] = 'High'
    alert = sm.services['alert']
    for fileName in fileAttachments:
        print fileName
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(fileName, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(fileName))
            msg.attach(part)
        except IOError as e:
            alert.LogInfo('File', fileName, 'could not be attached')

    callerFunctionName = sys._getframe(1).f_code.co_name
    alert.LogInfo(callerFunctionName + ' ', (len(message),
     recipients,
     subject,
     html))
    ctr = 0
    while not alert.SendMail(sender, recipients, msg.as_string(0), wait=True):
        ctr += 1
        if ctr > 9:
            break



exports = {'systemTest.SendSummaryMail': SendSummaryMail}

