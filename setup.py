from setuptools import setup, find_packages
import os
import shop_stripe

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    author="Jacob Rief",
    author_email="jacob.rief@gmail.com",
    name='django-shop-stripe',
    version=shop_stripe.__version__,
    description='Stripe Payment Provider Integration for django-shop',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    url='https://github.com/jrief/django-shop-stripe',
    license='MIT License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.7',
        #'django-shop>=0.3.0',
        'stripe>=1.26.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
