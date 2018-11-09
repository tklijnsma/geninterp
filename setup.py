from setuptools import setup

setup(name='geninterp',
      version='0.1',
      description='Generic interpreter',
      url='https://github.com/tklijnsma/geninterp.git',
      author='Thomas Klijnsma',
      author_email='thomasklijnsma@gmail.com',
      packages=['geninterp'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=[
        # 
        ]
      )