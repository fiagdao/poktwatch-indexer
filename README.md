# how to run

docker-compose up -d

there is probably a 75% chance that this won't work first try, so msg me on telegram @p1errre and i'll help you out.



## how it works

there is a postgres database running on the machine, this holds all the indexed data etc

there is pocket node with a custom config and custom pocket version enabled with more support for decoding pending transactions (this is a custom modification).

the backend script queries the pocket node and adds the indexed data to the database

the ./poktwatch directory is the frontend, which connects to the database and the pocket node for returning data.



if you guys want/need a fully complete database lmk, and if there are any other issues let me know. 
