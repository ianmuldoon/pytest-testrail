from setuptools import setup

INSTALL_REQUIREMENTS = 'requirements/base.txt'


def read_file(fname):
    with open(fname) as f:
        return f.read()


def get_requirements(*files):
    requirements = set()
    for file in files:
        for requirement in read_file(file, split_lines=True):
            requirements.add(requirement)
    return list(requirements)


setup(
    name='pytest-testrail',
    description='pytest plugin for creating TestRail runs and adding results + screenshots',
    long_description=read_file('README.rst'),
    version='2.9.0',
    author='Allan Kilpatrick / Ian Muldoon',
    author_email='allanklp@gmail.com, ian.muldoon@gmail.com',
    url='http://github.com/ianmuldoon/pytest-testrail/',
    packages=[
        'pytest_testrail',
    ],
    package_dir={'pytest_testrail': 'pytest_testrail'},
    install_requires=get_requirements(INSTALL_REQUIREMENTS),
    include_package_data=True,
    entry_points={'pytest11': ['pytest-testrail = pytest_testrail.conftest']},
)
