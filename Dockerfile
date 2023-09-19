FROM python:3.10-slim-buster

ARG VERSION="0.2.0"
ARG SIMULATOR_VERSION="2.72"

LABEL \
    org.opencontainers.image.authors="Alexander Patrie <apatrie@uchc.edu>, BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.title="biosimulators_simularium" \
    org.opencontainers.image.version="${SIMULATOR_VERSION}" \
    org.opencontainers.image.description="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format." \
    org.opencontainers.image.source="https://github.com/biosimulators/Biosimulators_tellurium" \
    org.opencontainers.image.authors="BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.vendor="BioSimulators Team" \
    org.opencontainers.image.licenses="Apache-2.0" \
    \
    base_image="python:3.9-slim-buster" \
    version="${VERSION}" \
    software="tellurium" \
    software.version="${SIMULATOR_VERSION}" \
    about.summary="Python-based environment for model building, simulation, and analysis that facilitates reproducibility of models in systems and synthetic biology" \
    about.home="http://tellurium.analogmachine.org/" \
    about.documentation="https://tellurium.readthedocs.io/" \
    about.license_file="https://github.com/sys-bio/tellurium/blob/develop/LICENSE.txt" \
    about.license="SPDX:Apache-2.0" \
    about.tags="kinetic modeling,dynamical simulation,systems biology,biochemical networks,SBML,SED-ML,COMBINE,OMEX,BioSimulators" \
    maintainer="BioSimulators Team <info@biosimulators.org>"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install smoldyn \
    && pip install . \
    && rm -rf /root/.cache/pip/

CMD ["python", "your_main_script.py"]