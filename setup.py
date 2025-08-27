from setuptools import find_packages, setup

setup(
    name='netbox-azure-groups',
    version='0.1.0',
    description='NetBox plugin for managing Azure AD groups and memberships',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BrynjarFAune/netbox-azure-groups',
    author='Brynjar F. Aune',
    author_email='brynjar.aune@example.com',
    license='Apache 2.0',
    install_requires=[
        'netbox>=3.0.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
)