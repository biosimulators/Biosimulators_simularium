pip install setuptools wheel twine \
      && python setup.py sdist bdist_wheel \
      && twine check dist/* \
      && twine upload dist/* \
      && rm -r dist \
      && rm -r build \
      && rm -r biosimulators_simularium.egg-info
