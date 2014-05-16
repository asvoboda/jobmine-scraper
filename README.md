#Jobminer

Simple python command line tool to search Jobmine with given criteria for jobs. Builds output based on inverse [joblinting] (http://joblint.org/) for the competitive sounding and hollow benefit co-op positions. 

Sample Usage
```
python jobminer.py -d1 COMP -d2 SOFT -s 1149 asvoboda
```

`python jobminer.py --help`

```
usage: jobminer.py [-h]
                   [-d1 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}]
                   [-d2 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}]
                   [-d3 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}]
                   [-t TITLE] [-e EMPLOYER] [-s SESSION]
                   username

Search and login options for jobmine

positional arguments:
  username              your uwaterloo username

optional arguments:
  -h, --help            show this help message and exit
  -d1 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}, --discipline1 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}
                        discipline 1 code
  -d2 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}, --discipline2 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}
                        discipline 2 code
  -d3 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}, --discipline3 {TRON,COMP,MECH,UNSP,CIV,ENV,CHEM,ELEC,NANO,SOFT,SYDE,GEO,MAN}
                        discipline 3 code
  -t TITLE, --title TITLE
                        job title search string
  -e EMPLOYER, --employer EMPLOYER
                        employer search string
  -s SESSION, --session SESSION
                        job session number, ex: 1149 = [1] 20[14] September[9]
```