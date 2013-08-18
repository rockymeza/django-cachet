import os
import sys

from setuptools import setup

version = __import__('cash').get_version()

install_requires = ['Django>=1.3']
tests_require = []

if sys.version_info[0] < 3:
    tests_require.append('mock')


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(name='django-cash',
      version=version,
      author="Rocky Meza",
      author_email="rockymeza@gmail.com",
      url="https://github.com/fusionbox/django-cash",
      keywords="django cache templatetag",
      description="Caching helpers for Django",
      long_description=read_file('README.rst'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ],
      install_requires=install_requires,
      tests_require=tests_require,
      packages=[
          'cash',
          'cash.templatetags',
      ],

      test_suite='testproject.runtests',
)
