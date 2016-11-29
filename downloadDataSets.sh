#!/bin/bash

mkdir -p dataset 

declare -A data

# World Jiu-Jitsu IBJJF Championship
data["000535"]="world-gi-2016.pdf"
data["000415"]="world-gi-2015.pdf"
data["000272"]="world-gi-2014.pdf"
data["000177"]="world-gi-2013.pdf"
data["000114"]="world-gi-2012.pdf"

# World Master Jiu-Jitsu IBJJF Championship
data["000572"]="worldmaster-gi-2016.pdf"
data["000450"]="worldmaster-gi-2015.pdf"
data["000318"]="worldmaster-gi-2014.pdf"
data["000211"]="worldmaster-gi-2013.pdf"
data["000140"]="worldmaster-gi-2012.pdf"

 #World Jiu-Jitsu No-Gi IBJJF Championship
data["000625"]="world-nogi-2016.pdf"
data["000461"]="world-nogi-2015.pdf"
data["000313"]="world-nogi-2014.pdf"
data["000217"]="world-nogi-2013.pdf"
data["000149"]="world-nogi-2012.pdf"

# European Jiu-Jitsu IBJJF Championship
data["000490"]="europa-gi-2016.pdf"
data["000352"]="europa-gi-2015.pdf"
data["000232"]="europa-gi-2014.pdf"
data["000154"]="europa-gi-2013.pdf"

# European Jiu-Jitsu No-Gi IBJJF Championship
data["000518"]="europa-nogi-2016.pdf"
data["000377"]="europa-nogi-2015.pdf"
data["000243"]="europa-nogi-2014.pdf"
data["000181"]="europa-nogi-2013.pdf"
data["000142"]="europa-nogi-2012.pdf"

# Berlin International Open IBJJF Jiu-Jitsu Championship
data["000465"]="berlin-gi-2015.pdf"

# Berlin International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000466"]="berlin-nogi-2015.pdf"

# British National IBJJF Jiu-Jitsu Championship
data["000555"]="britain-gi-2016.pdf"
data["000399"]="britain-gi-2015.pdf"

# British National IBJJF Jiu-Jitsu No-Gi Championship
data["000556"]="britain-nogi-2016.pdf"
data["000400"]="britain-nogi-2015.pdf"

# Copenhagen International Open IBJJF Jiu-Jitsu Championship
data["000260"]="copenhagen-gi-2014.pdf"

# Copenhagen International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000261"]="copenhagen-nogi-2014.pdf"

# Madrid International Open IBJJF Jiu-Jitsu Championship
data["000473"]="madrid-gi-2015.pdf"
data["000326"]="madrid-gi-2014.pdf"

# Madrid International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000643"]="madrid-nogi-2016.pdf"
data["000474"]="madrid-nogi-2015.pdf"

# Moscow International Open
data["000324"]="moscow-gi-2014.pdf"

# Moscow International Open No-Gi
data["000325"]="moscow-nogi-2014.pdf"

# Munich International Open IBJJF Jiu-Jitsu Championship
data["000509"]="munich-gi-2016.pdf"
data["000219"]="munich-gi-2013.pdf"

# Munich International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000509"]="munich-nogi-2016.pdf"

# Munich Winter International Open IBJJF Jiu-Jitsu Championship
data["000366"]="munichwinter-gi-2015.pdf"
data["000247"]="munichwinter-gi-2014.pdf"

# Munich Winter International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000367"]="munichwinter-nogi-2015.pdf"

# Munich Fall International Open IBJJF Jiu-Jitsu Championship
data["000319"]="munichfall-gi-2014.pdf"

# Paris International Open IBJJF Jiu-Jitsu Championship
data["000289"]="paris-gi-2014.pdf"

# Paris International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000290"]="paris-nogi-2014.pdf"

# Rome International Open IBJJF Jiu-Jitsu Championship
data["000517"]="rome-gi-2016.pdf"
data["000376"]="rome-gi-2015.pdf"
data["000242"]="rome-gi-2014.pdf"
data["000180"]="rome-gi-2013.pdf"

# Spanish National IBJJF Jiu-Jitsu Championship
data["000547"]="spain-gi-2016.pdf"

# Spanish National IBJJF Jiu-Jitsu No-Gi Championship
data["000548"]="spain-nogi-2016.pdf"

# Zadar International Open IBJJF Jiu-Jitsu Championship
data["000298"]="zadar-gi-2014.pdf"

# Zurich International Open IBJJF Jiu-Jitsu Championship
data["000537"]="zurich-gi-2016.pdf"
data["000389"]="zurich-gi-2015.pdf"
data["000262"]="zurich-gi-2014.pdf"

# Zurich International Open IBJJF Jiu-Jitsu No-Gi Championship
data["000538"]="zurich-nogi-2016.pdf"
data["000390"]="zurich-nogi-2015.pdf"

for key in ${!data[@]}; do 
    FILE="${key}-${data["${key}"]}"
    wget "http://static.ibjjfdb.com/Campeonato/$key/en-US/Results.pdf" -O "dataset/result-$FILE"
    #wkhtmltopdf --no-background --no-images "https://www.ibjjfdb.com/ChampionshipResults/$key/PublicAcademyRegistration?lang=en-US" "dataset/academy-$FILE"
    #wkhtmltopdf --no-background --no-images "https://www.ibjjfdb.com/ChampionshipResults/$key/PublicRegistrations?lang=en-US" "dataset/division-$FILE" 
done



