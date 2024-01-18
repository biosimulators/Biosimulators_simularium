FROM python:3.10

LABEL \
    org.opencontainers.image.authors="Alexander Patrie <apatrie@uchc.edu>, BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.title="biosimulators_simularium"
    # org.opencontainers.image.description="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    # org.opencontainers.image.source="https://github.com/biosimulators/Biosimulators_simularium" \
    # org.opencontainers.image.vendor="BioSimulators Team" \
    # org.opencontainers.image.licenses="MIT" \
    # base_image="python:3.10" \
    # version="${VERSION}" \
    # about.summary="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    # about.home="https://github.com/biosimulators/Biosimulators_simularium" \
    # about.license_file="https://github.com/biosimulators/Biosimulators/blob/dev/LICENSE.txt" \
    # about.license="MIT" \
    # about.tags="spatial simulations, particle-based simulations, molecular diffusion, surface interactions, chemical reactions, SBML, SED-ML, COMBINE, OMEX, BioSimulators"

RUN apt-get update && apt-get install -y build-essential libxml2-dev libzip-dev

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry run pip install pyomexmeta

RUN chmod +x /app/install.sh

RUN /bin/bash -c '/app/install.sh'

# RUN /app/install.sh

ENTRYPOINT ["biosimulators-simularium"]

CMD ["poetry run ipython3"]


# RUN pip install --upgrade pip \
#     && pip install setuptools wheel twine \
#     && python /app/setup.py sdist bdist_wheel \
#     && twine check dist/* \
#     && twine upload dist/* \
#     && rm -r dist \
#     && rm -r build \
#     && rm -r biosimulators_simularium.egg-info
