from setuptools import setup

setup(name='labjackcontroller',
      version='0.1',
      description='A helper library to control LabJack devices',
      packages=['labjackcontroller'],
      licence='MIT',
      install_requires=[
                        'typing',
                        'numpy'
                       ],
      zip_safe=False)
