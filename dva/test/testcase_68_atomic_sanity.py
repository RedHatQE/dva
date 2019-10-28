""" This module contains  68_atomic_sanity test """
from testcase import Testcase
from dva.work.common import RESULT_FAILED


class testcase_68_atomic_sanity(Testcase):
    """
    Test whether Atomic AMI is ready for release
    """
    stages = ['stage1']
    tags = ['default']
    applicable = {'virtualization': 'hvm', 'platform': '(?i)BETA|RHEL|ATOMIC', 'version': 'OS (>=7.2)'}

    def test(self, connection, params):

        product = params['product'].upper()
        if product != 'ATOMIC':
            return self.log

        if 'subscription_username' not in params or 'subscription_password' not in params:
            self.log.append({
                'result': RESULT_FAILED,
                'comment': 'the test requires valid Subscription manager credentials in dva.yaml config file, i.e.: \
                    cloud_access: \
                        subscription_manager: \
                            subscription_username: aaaaaa \
                            subscription_password: bbbbbb'})
            return self.log

        subscription_username = params['subscription_username']
        subscription_password = params['subscription_password']

        self.get_return_value(connection, 'subscription-manager register --serverurl=subscription.rhn.redhat.com:443/subscription --username=%s --password=%s --auto-attach --force' % (subscription_username, subscription_password), 360, nolog=True)
        self.get_return_value(connection, 'subscription-manager repos --disable=*', 180)
        self.get_return_value(connection, 'subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms', 180)
        self.get_return_value(connection, 'docker pull rhel7', 3600)
        self.get_result(connection, 'printf "FROM rhel7\nRUN yum -y install --disablerepo=* --enablerepo=rhel-7-server-rpms traceroute;yum clean all\nCMD [\\"traceroute\\",\\"google.com\\"]\n" > Dockerfile; echo ')
        self.get_return_value(connection, 'docker build --rm --no-cache --force-rm -t traceroute .', 360)
        self.get_return_value(connection, 'docker run --rm traceroute', 360)
        self.get_return_value(connection, 'docker rmi traceroute', 60)
        self.get_return_value(connection, 'docker rmi rhel7', 60)
        self.get_return_value(connection, 'subscription-manager unregister', 60)

        return self.log

