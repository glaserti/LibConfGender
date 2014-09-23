# after getting the data via Python, 
# quickly calculate & visualize absolute numbers & percentages
# based on the file summary.json

library(jsonlite)
confSpeak <- fromJSON('summary.json')

# Calculations
# absolute numbers
matr_abs <- matrix(c(confSpeak$female, confSpeak$male, confSpeak$undef),
                   byrow=TRUE, nrow=3,
                   dimnames = list(c('female', 'male', 'undef'),
                                   c('2009', '2010', '2011', '2012', '2013', '2014')))
print(matr_abs)

# percentages
sumPerYear <- confSpeak$male + confSpeak$female + confSpeak$undef
percentagesMale <- confSpeak$male * 100 / sumPerYear
percentagesFemale <- confSpeak$female * 100 / sumPerYear
percentagesUndef <- confSpeak$undef * 100 / sumPerYear
percentages <- c(percentagesMale, percentagesFemale, percentagesUndef)


# Plotting the total numbers
barplot(matr_abs, main = "Präsentationen von Frauen/Männern 2009 - 2014",
        col = c('red3','dodgerblue3', 'limegreen'))

# Plotting the percentages
matr_perc <- matrix(c(percentagesFemale, percentagesMale, percentagesUndef),
               byrow=TRUE, nrow=3,
               dimnames = list(c('female', 'male', 'undef'),
                               c('2009', '2010', '2011', '2012', '2013', '2014')))
barplot(matr_perc, main = "Prozentuale Verteilung Frauen/Männer 2009 - 2014",
        col = c('red3','dodgerblue3', 'limegreen'))
abline(h=50, lty = 5, lwd = 3)