from setuptools import setup

setup(name='labjackcontroller',
      description='A helper library to control LabJack devices',
      version='0.1',
      url='https://github.com/Nyctanthous/labjack-controller',
      author='Ben Montgomery',
      packages=['labjackcontroller'],
      licence='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      install_requires=[
                        'typing',
                        'numpy',
                        'pandas',
                        'colorama'
                       ],
      zip_safe=False)
