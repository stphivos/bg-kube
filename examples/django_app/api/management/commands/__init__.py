from subprocess import Popen, PIPE


def run(command):
    process = Popen('python manage.py {}'.format(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = process.communicate()

    assert not error, error

    result = output.decode('utf-8').strip()
    assert process.returncode == 0 or not result, process.returncode

    return result
