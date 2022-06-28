FROM ubuntu:20.04

# Label
LABEL org.opencontainers.image.title="fish cropping and trait morphology"
LABEL org.opencontainers.image.authors=" T. Tabarin"
LABEL org.opencontainers.image.source="https://github.com/hdr-bgnn/BGNN_Snakemake"

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    wget \
 && rm -rf /var/lib/apt/lists/*

# Create a working directory
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod 777 /home/user

# Set up the Conda environment
ENV CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/home/user/miniconda/bin:$PATH
COPY morphology_env.yml /app/environment.yml
RUN curl -sLo ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh \
 && conda env update -n base -f /app/environment.yml \
 && rm /app/environment.yml \
 && conda clean -ya

WORKDIR /pipeline

# Setup pipeline specific scripts
ENV PATH="/pipeline/Morphology:${PATH}"
ENV PATH="/pipeline/Crop:${PATH}"
ENV PATH="/pipeline/Merge_files:${PATH}"
ADD Crop_image/Crop_image_main.py /pipeline/Crop/Crop_image_main.py
ADD Morphology/Traits_class.py /pipeline/Morphology/Traits_class.py
ADD Morphology/Morphology_main.py /pipeline/Morphology/Morphology_main.py
ADD Merge_files/Merge_files_main.py /pipeline/Merge_files/Merge_files_main.py

# Set the default command to a usage statement
CMD echo "Usage crop: Crop_image_main.py <input_image.jpg> <image_metadata.json> <image_cropped.png>\n"\
"Usage Morphology: Morphology_main.py  <input_file> <measure.json> <landmark.json> <presence.json> <image_lm.png>\n"\
"Usage Merge_file: Merge_files_main.py  <input_directory> <merge.csv> <merge.json>"
