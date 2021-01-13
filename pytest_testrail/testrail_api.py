"""TestRail API binding for Python 3.x.
(API v2, available since TestRail 3.0)
Compatible with TestRail 3.0 and later.
Learn more:
http://docs.gurock.com/testrail-api2/start
http://docs.gurock.com/testrail-api2/accessing
Copyright Gurock Software GmbH. See license.md for details.
"""

import base64
import json
from urllib.parse import urljoin

import requests


class APIClient:

    def __init__(self, base_url, user, password, **kwargs):
        """
        Instantiate the APIClient class.

        :param base_url: The same TestRail address for the API client you also use to access TestRail with your web
            browser (e.g., https://<your-name>.testrail.com/ or http://<server>/testrail/).
        :type base_url: str
        :param user: Username for the account on the TestRail server.
        :type user: str
        :param password: Password for the account on the TestRail server.
        :type password: str
        :param headers: (optional) Dictionary of HTTP Headers to send with each request.
        :type headers: dict
        :param cert_check: (optional) Either a boolean, in which case it controls whether we verify the server's TLS
            certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
        :type cert_check: bool or str
        :param timeout: (optional) How many seconds to wait for the server to send data before giving up, as a float,
            or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        """
        self.__url = urljoin(base_url, 'index.php?/api/v2/')
        self.user = user
        self.password = password
        self.headers = kwargs.get('headers', {'Content-Type': 'application/json'})
        self.cert_check = kwargs.get('cert_check', True)
        self.timeout = kwargs.get('timeout', 10.0)
        if self.timeout is not None:
            self.timeout = isinstance(self.timeout, float) if False else float(self.timeout)

    def send_get(self, uri, filepath=None, **kwargs):
        """Issue a GET request (read) against the API.
        Args:
            uri: The API method to call including parameters, e.g. get_case/1.
            filepath: The path and file name for attachment download; used only
                for 'get_attachment/:attachment_id'.
        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('GET', uri, filepath, **kwargs)

    def send_post(self, uri, data, **kwargs):
        """Issue a POST request (write) against the API.
        Args:
            uri: The API method to call, including parameters, e.g. add_case/1.
            data: The data to submit as part of the request as a dict; strings
                must be UTF-8 encoded. If adding an attachment, must be the
                path to the file.
        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('POST', uri, data, **kwargs)

    def __send_request(self, method, uri, data, **kwargs):
        url = self.__url + uri
        cert_check = kwargs.get('cert_check', self.cert_check)

        auth = str(
            base64.b64encode(
                bytes('%s:%s' % (self.user, self.password), 'utf-8')
            ),
            'ascii'
        ).strip()
        headers = {'Authorization': 'Basic ' + auth}

        if method == 'POST':
            if uri[:14] == 'add_attachment':    # add_attachment API method
                files = {'attachment': (open(data, 'rb'))}
                response = requests.post(url, headers=headers, files=files)
                files['attachment'].close()
            else:
                headers['Content-Type'] = 'application/json'
                payload = bytes(json.dumps(data), 'utf-8')
                response = requests.post(
                    url,
                    headers=headers,
                    data=payload,
                    verify=cert_check,
                    timeout=self.timeout
                )
        else:
            headers['Content-Type'] = 'application/json'
            response = requests.get(
                url,
                headers=headers,
                verify=cert_check,
                timeout=self.timeout
            )

        if response.status_code > 201:
            return response
        else:
            if uri[:15] == 'get_attachment/':   # Expecting file, not JSON
                return self.save_attachment(data, response)
            else:
                return response

    @staticmethod
    def save_attachment(data, response):
        try:
            open(data, 'wb').write(response.content)
            return data
        except Exception as ee:
            return f"Error saving attachment: {ee}"

    @staticmethod
    def get_error(json_response):
        """ Extract error contained in a API response.
            If no error occurred, return None

            :param json_response: json response of request
            :return: String of the error
        """
        if 'error' in json_response and json_response['error']:
            return json_response['error']


class APIError(Exception):
    pass

