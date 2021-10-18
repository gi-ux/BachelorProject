# Bachelor Project

This project was carried out as a diploma project for SUPSI.

It involves studying of the peculiar behaviors of harmful entities in the COVID 19 debate to provide social change towards a better understanding (literacy) of social networks. 

## Tasks

- Identification of tools used for news propagation
- Identification and classification of entities in the discussion
- Behavioral analysis of malicious entities and comparison with competent entities

## Objectives

The main objective of this thesis is to come to distinguish the strategies and impact of correct and malicious entities/actions in the COVID19 debate.
To then identify through which means and behaviors the various malicious entities influence the discussions by analyzing hashtags, shared links, and activities, making a comparison between those whose goal is to inform correctly and those who intentionally spread untrue information.

## Technologies

- Python (wide use of Notebooks)
- Complex networks

## Project structure

To have a better management of the project, different folders have been created:
- notebook folder contains all Notebooks and .py files
- doc folder contains information regarding the progress and implementation of the project, this folder also houses reports for the project display.
- csv folder contains miscellaneous .csv files used
Some folders are kept offline for size and privacy reasons.

## Privacy

Since the data in question is public information on an open platform that can be viewed even without registering with Twitter, there are no privacy-related issues in sharing it. However, the information that was considered confidential was kept offline.

## Data Collection

Data are collected through an [existing repository](https://github.com/echen102/COVID-19-TweetIDs) on which a hydration process has been done).

## External Tools

#### Media Bias/Fact Check

For the study of veracity of a shared domain a factchecking tool was used that allows to give a "credibility" score.
Through this score it was possible to obtain a list of domains with high credibility and others with low credibility, distinguishing authoritative and non-authoritative sources.

More info on https://mediabiasfactcheck.com/.


#### Botometer

Since during the project there was an interest in collecting information about potential bots in the discussion, a tool was used to give a score from 1 to 0 that represents the probability that a user is a bot or not.

The tool can be accessed through the [website](https://botometer.osome.iu.edu/) or through a special API.

More information is available on the [GitHub repository of Botometer](https://github.com/IUNetSci/botometer-python).

## Partial Results

Through this study it was possible to classify users according to their position within the discussion from Covid-19 on Twitter. 

It was possible to identify the main actors of misinformation and the corresponding actors of good information, obtaining valuable information on shared domains, information strategies and hashtags used.
It was possible to identify the bots in play, going to give an interesting classification of these and identify them in the discussion, they are in fact mainly engaged in information sharing operations without particular interest in influencing the discussion.

Starting with this information, it is possible to be able to identify and act against actions that lead to the propagation and proliferation of fake news of any kind related to the Covid-19 discussion. This would give the possibility to improve the quality of information in circulation, thus limiting the visibility that incorrect users have. All this can also play an important role on the health of citizens who use social networks to inform themselves.