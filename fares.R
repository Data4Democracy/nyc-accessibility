library("tidyverse")
library("httr")
library("tidyr")
library("rvest")
library("dplyr")

#set the config to get around self-sign error
httr::set_config( config( ssl_verifypeer = 0L ) )

#set the URL to the main page that lists links to fare data by week
URL<-"http://web.mta.info/developers/fare.html"

#get the list of links to each weeks data
faresite<-httr::content(GET(URL))

#get the text of each link, which is a day-date
faredate<-faresite %>% 
  html_nodes(".last a") %>% 
  html_text()

#extract the URL for each link
farelink<-faresite %>%
  html_nodes(".last a") %>% 
  html_attr("href")

#bind the two lists together to create a table with the date and link
faretbl<-as.data.frame(cbind(date=faredate, link=farelink), stringsAsFactors = FALSE)

#format the date to remove the weekday info
faretbl$date<-lubridate::mdy(faretbl$date)

#each link is relative, paste the suffix to create a full absolute path
faretbl$link<-paste0("http://web.mta.info/developers/", faretbl$link)



#scrape the first 52 (one year's worth) records' data
fares<-lapply(faretbl$link[1:381], read.csv, stringsAsFactors=FALSE, skip=2)

#after looking at the data, there were some inconsistencies due to new fare types being introduced over the past year.  There are a total of 25 fare types, but many of them either had a column total of zero or are fare types that aren't relevant to our analysis (e.g., mta employee fares, AirTrain, CUNY student special fare, etc.) I kept the full fare, senior discount, AFAS (ADA) and the weekly and monthly card data

#use purrr to get just the first 12 columns
fares<-map(fares, `[`, c("STATION","FF","SEN.DIS","X7.D.AFAS.UNL","X30.D.AFAS.RMF.UNL", "JOINT.RR.TKT", "X7.D.UNL", "X30.D.UNL",  "TCMC"))

fares<-bind_rows(fares, .id="group")
names(fares)<-tolower(names(fares))
fares$wktot<-rowSums(fares[,3:10])

#remove depot and select bus service names
fares<-fares %>% filter(!grepl("DEPOT", station) & !grepl("@", station) & station !="MTABC - EASTCHESTER 2")

#create a table with seq_along data and the date to join the date back in after binding the list elements together
fare_group_for_join<-data.frame(date=as.Date(faretbl$date), group=as.character(seq_along(faretbl$date)))

#add dates back to the df
fares<-left_join(fares, fare_group_for_join, by="group")


adanames<-names(fares)[grepl("afas", names(fares))]
ada<-fares %>% select(station, date, adanames)
write.csv(fares, "E:/d4d/fare_history.csv", row.names=FALSE)


