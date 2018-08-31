from setuptools import setup
import setuptools

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='deepeye_pack',
      version='0.1',
      description='a Python package for DeepEye:Towards automatic Data Visualization API',
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      url='https://github.com/TsinghuaDatabaseGroup/DeepEye/tree/master/APIs_Deepeye',
      author='tpchris1',
      author_email='topchrischang@hotmail.com',
      license='MIT',
      packages=setuptools.find_packages(),
      install_requires=[
          'numpy',
          'pandas',
          'MySQLdb',
          'pyecharts',
          'pprint'
      ],
      
      include_package_data=True,
      zip_safe=False)