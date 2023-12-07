from setuptools import setup, find_packages

setup(
      name='ropac',
      version='0.0.1',
      author='Erik H. Becker',
      author_email='Erik_BECKER@nea.gov.sg',
      description='A description of my package',
      packages=find_packages(),
      install_requires=[
            'wradlib',
            'h5py',
            'matplotlib',
            'numpy',
      ],
      package_data={'ropac': [
                        'config/*.yaml',
                        'config/*.ini',
                        'utils/*.yaml',
                        'stats/*.yaml'
                        ],
      },
      include_package_data=True,
      # entry_points={
      #       'console_scripts': [
      #             'my_script=my_package.main:main'
      #       ]
      # },
      # classifiers=[
      #       'Development Status :: 3 - Alpha',
      #       'Intended Audience :: Developers',
      #       'Programming Language :: Python :: 3',
      #       'Programming Language :: Python :: 3.6',
      #       'Programming Language :: Python :: 3.7',
      #       'Programming Language :: Python :: 3.8',
      #       'Programming Language :: Python :: 3.9',
      # ],
      )
