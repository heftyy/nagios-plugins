from setuptools import setup

setup(
        name="appname",
        version="100",
        description="yadda yadda",
        author="myself and I",
        author_email="email@someplace.com",
        url="whatever",
        # Name the folder where your packages live:
        # (If you have other packages (dirs) or modules (py files) then
        # put them into the package directory - they will be found
        # recursively.)
        packages=['plugins'],
        long_description="""Really long text here.""",
        #
        # This next part it for the Cheese Shop, look a little down the page.
        # classifiers = []
        scripts=['plugins/notify.py'],
        entry_points={
            'console_scripts': [
                'notify = plugins.notify:notify',
            ]
        }, requires=['requests', 'pysnmp']
)
