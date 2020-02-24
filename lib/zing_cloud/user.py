'''
Copyright 2017, Zingbox, http://zingbox.com

Date: 8/24/2017 09:13:00

Author: Jeffrey LEE
'''
import os
import sys
import time
from datetime import datetime

from . import Utils

db = None
log_template = 'Operation: {0}, params: {1}\n'

def setup():
    """setup function abstracts Utils to create a
        pymongo.database.Database instance. And it also handles setup config
        for user script.
    """
    global db
    db = Utils.DB.getConnection()

def teardown():
    """teardown function abstracts Utils to create a
        pymongo.database.Database instance. And it also handles teardown config
        for user script.
    """
    global db
    Utils.DB.closeConnection()
    db = None

def main():
    """main function is run after verifying the environment is in testing.

        This is the main flow of the script. Expecting to parse an option and
        carry out respective actions, such as, --help, --delete-user. It acts as
        a distributor to delegate jobs to different functions. It also call
        setup() and teardown() scripts because this is the main flow of the
        script itself.
    """
    arguments = _get_arguments()
    if type(arguments) != list or len(arguments) < 1:
        print('Error: No operations, please specify arguments.')
        _print_help()
        sys.exit()

    setup()
    if db is None:
        print('Error: Database connection failed. No operations.')
        return

    operation = str(arguments[0])
    if operation == '--delete-user':
        delete_user(arguments[1:])
    elif operation == '--delete-reseller':
        delete_reseller(arguments[1:])
    elif operation == '--delete-tenant':
        delete_tenant(arguments[1:])
    elif operation == '--delete-trial-user':
        delete_trial_user(arguments[1:])
    elif operation == '--mark-trial-user-ready':
        mark_trial_user_ready(arguments[1:])
    elif operation == '--help':
        _print_help()
    else:
        print(('Error: operation {} not recognized.'.format(operation)))
        _print_help()

    teardown()

def _validate_email_to_be_deleted(collection, email, key='username'):
    """_validate_email_to_be_deleted function validates if a user exists in a
        collection.

        This function takes a pymongo.collection.Collection object and check if
        the input email exists in that collection. Also, it makes sure that we
        validate the email contains keyword 'zbat'. It is developers'
        responsibility to call this function if they want to validate an email.
        Keyword configuration is not generally restricted. But this function
        will do the job, if developer don't want to validate the email, it is
        their choice.

            :param collection: The collection that you want to verify the email.
            :type collection: pymongo.collection.Collection
            :param email: Email to verify.
            :type email: str
            :param key: Key of collection that direct to email.
            :type email: str
            :return: return Does the email exist in collection
            :rtype: bool
    """
    if 'zbat' not in email:
        print('Error: Only able to delete user with \'zbat\' in email.')
        return False
    query = {
        key: email
    }
    options = {
        'justOne': True
    }
    user = collection.find_one(query, options)
    if user is None:
        print(('Error: No user with email {}.'.format(email)))
        return False
    return True

def delete_user(emails):
    """delete_user is called when --delete-user operation is parsed from input
        arguments. It deletes a list of emails from user collection. And it also
        create a log record for this action.

        It is important to note that currently this function only support list
        of one email. This approach is planned for future if we want to support
        deleting multiple emails.

            :param emails: List of emails to be deleted in user collection.
            :type emails: list of str
    """
    try:
        _verify_env()
    except Exception as err:
        print(err)
        sys.exit()
    if type(emails) != list:
        print('Error: not able to parse email to be deleted.')
        return
    if len(emails) != 1:
        print('Error: Please specify one and only one user to be deleted.')
        return
    email = str(emails[0])
    col = db.user
    if _validate_email_to_be_deleted(col, email) is False:
        return
    query = {
        'username': email
    }
    options = {
        'justOne': True
    }
    col.remove(query, options)
    _write_log(log_template.format('delete_user', email))

def delete_reseller(emails):
    """delete_reseller is called when --delete-reseller operation is parsed
        from input arguments. It deletes a list of emails from user collection.
        And it also create a log record for this action.

        It is important to note that currently this function only support list
        of one email. This approach is planned for future if we want to support
        deleting multiple emails.

            :param emails: List of emails to be deleted in reseller collection.
            :type emails: list of str
    """
    try:
        _verify_env()
    except Exception as err:
        print(err)
        sys.exit()
    if type(emails) != list:
        print('Error: not able to parse email to be deleted.')
        return
    if len(emails) != 1:
        print('Error: Please specify one and only one user to be deleted.')
        return
    email = str(emails[0])
    col = db.Reseller
    if _validate_email_to_be_deleted(col, email) is False:
        return
    query = {
        'username': email
    }
    options = {
        'justOne': True
    }
    col.remove(query, options)
    _write_log(log_template.format('delete_reseller', email))

def delete_tenant(emails):
    """delete_tenant is called when --delete-tenant operation is parsed
        from input arguments. It deletes list of emails from tenant collection.
        And it also create a log record for this action.

        It is important to note that currently this function only support list
        of one emails. This approach is planned for future if we want to support
        deleting multiple emails.

            :param emails: List of emails to be deleted in tenant collection.
            :type emails: list of str
    """
    try:
        _verify_env()
    except Exception as err:
        print(err)
        sys.exit()
    if type(emails) != list:
        print('Error: not able to parse email to be deleted.')
        return
    if len(emails) != 1:
        print('Error: Please specify one and only one tenant to be deleted.')
        return
    email = str(emails[0])
    col = db.Tenant
    key = 'owner'
    if _validate_email_to_be_deleted(col, email, key=key) is False:
        return
    query = {
        key: email
    }
    options = {
        'justOne': True
    }
    col.remove(query, options)
    _write_log(log_template.format('delete_tenant', email))

def delete_trial_user(emails):
    """delete_trial_user is called when --delete-trial-user operation is parsed
        from input arguments. It deletes list of emails from TrialUser
        collection. And it also create a log record for this action.

        It is important to note that currently this function only support list
        of one emails. This approach is planned for future if we want to support
        deleting multiple emails.

            :param emails: List of emails to be deleted in tenant collection.
            :type emails: list of str
    """
    try:
        _verify_env()
    except Exception as err:
        print(err)
        sys.exit()
    if type(emails) != list:
        print('Error: not able to parse email to be deleted.')
        return
    if len(emails) != 1:
        print('Error: Please specify one and only one tenant to be deleted.')
        return
    email = str(emails[0])
    col = db.TrialUser
    if _validate_email_to_be_deleted(col, email) is False:
        return
    query = {
        'username': email
    }
    options = {
        'justOne': True
    }
    col.remove(query, options)
    _write_log(log_template.format('delete_trial_user', email))

def mark_trial_user_ready(emails):
    """mark_trial_user_ready is called when --mark-trial-user-ready operation
        is parsed from input arguments. It updates list of emails from TrialUser
        collection, changing status filed to 'IMAGE_READY'. And it also create
        a log record for this action.

        It is important to note that currently this function only support list
        of one emails. This approach is planned for future if we want to support
        deleting multiple emails.

            :param emails: List of emails to be deleted in tenant collection.
            :type emails: list of str
    """
    try:
        _verify_env()
    except Exception as err:
        print(err)
        sys.exit()
    if type(emails) != list:
        print('Error: not able to parse email to be deleted.')
        return
    if len(emails) != 1:
        print('Error: Please specify one and only one tenant to be deleted.')
        return
    email = str(emails[0])
    col = db.TrialUser
    query = {
        'username': email
    }
    update = {
      '$set': {
        'status': 'IMAGE_READY'
      }
    }
    col.update(query, update)
    _write_log(log_template.format('mark_trial_user_ready', email))

def _get_arguments():
    """_get_arguments retrieve arguments passed from command line.

            :return: return list of arguments passed from command line.
            :rtype: list of str
    """
    return sys.argv[1:]

def _print_help():
    """_print_help prints well documented message to guide user of this user.py.
        Usage:
            - python user.py
            - python user.py --help
            - python user.py <whatever operation not supportted>
    """
    print('\n')
    print('usage: python user.py [options]\n')
    print('\n')
    _print_argument_help(
        '    --delete-user <email>',
        'Delete a single user. Since this is dangerous, we only support ' +
            'deleting one user at a time. Plus, the user to be deleted must ' +
            'includes \'zbat\' keyword in email.'
    )
    _print_argument_help(
        '    --delete-reseller <email>',
        'Delete a single reseller. Since this is dangerous, we only support ' +
            'deleting one reseller at a time. Plus, the user to be deleted ' +
            'must ncludes \'zbat\' keyword in email.'
    )
    _print_argument_help(
        '    --delete-tenant <owner-email>',
        'Delete a single tenant. Since this is dangerous, we only support ' +
            'deleting one tenant at a time. Plus, the user to be deleted ' +
            'must includes \'zbat\' keyword in email.'
    )
    _print_argument_help(
        '    --delete-trial-user <email>',
        'Delete a single trial user. Since this is dangerous, we only ' +
            'support deleting one trial user at a time. Plus, the user to be ' +
            'deleted must includes \'zbat\' keyword in email.'
    )
    _print_argument_help(
        '    --mark-trial-user-ready <email>',
        'Mark a single trial user\'s status to "IMAGE_READY". Since this is ' +
            'dangerous, we only support editing one trial user at a time. ' +
            'Plus, the user to be editted must includes \'zbat\' keyword in ' +
             'email.'
    )
    _print_argument_help(
        '    --help',
        'print this help message.'
    )
    print('\n')

def _print_argument_help(operation, description):
    """_print_argument_help is a helper function for _print_help() to print
        operations. DRY approach.

            :param operation: Operation name
            :type operation: str
            :param description: Description of the operation
            :type operation: str
    """
    print(('{:<30} {:<30}'.format(operation, description)))

def _write_log(message):
    """_write_log function export a log message to user.log file to trace
        actions carried out by user.py.

            :param message: Message to be logged.
            :type message: str
    """
    with open('user.log','ab') as f:
        f.write('{0} {1}'.format(_get_timestamp(), message))

def _get_timestamp():
    """_get_timestamp function returns a human readable time.

            :return: return readable time in format '%m/%d/%Y %H:%M:%S %Z'.
            :rtype: str
    """
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime('%m/%d/%Y %H:%M:%S %Z')

def _verify_env():
    """_verify_env is called to make sure that the env is in testing.
        Throughs error when NODE_ENV is not is testing.
    """
    env = os.environ['NODE_ENV']
    if env is None or type(env) != str:
        raise Exception('Error: Please specify "NODE ENV".')
    elif 'testing' not in env and 'staging' not in env:
        raise Exception('Error: Script MUST not run in non testing or non staging env.')

if __name__ == '__main__':
    try:
        _verify_env()
    except Exception as err:
        print(err)
        sys.exit()
    env = os.environ['NODE_ENV']
    if 'testing' in env:
        main()
