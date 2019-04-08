from setuptools import setup

setup(name='labjackcontroller',
      description='A helper library to control LabJack devices',
      version='0.3',
      url='https://github.com/Nyctanthous/labjack-controller',
      author='Ben Montgomery',
      packages=['labjackcontroller'],
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      dependency_links=[
                        'https://github.com/labjack/labjack-ljm-python/tarball/master',
                       ],
      install_requires=[
                        'typing',
                        'numpy',
                        'pandas',
                        'colorama',
                        'labjack-ljm'
                       ],
      zip_safe=False)
