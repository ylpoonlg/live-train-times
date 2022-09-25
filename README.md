# live-train-times
A simple train station LED board emulator.

### Setting Up
#### Install python dependencies

    $ pip3 install -r requirements.txt

#### Configuration
Create a new config file by copying the default template file.

    $ cp default_config.py config.py
    
Open ```config.py``` and replace the value of ```LDBWS_TOKEN``` with your own token.

### Running

    $ python3 main.py
    
#### Options
##### Selecting station
By default, the station is Manchester Piccadilly (crs: MAN). You can set it to another station by providing the CRS code, e.g.

    $ python3 main.py --crs EUS
    
for London Euston station.

#### For the full list of options, run ```python3 main.py --help```

### Future Plans
- [ ] Different panel styles
- [ ] Arrival board
- [ ] Platform board
