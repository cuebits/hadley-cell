# Loads the trend package from CRAN
require(trend)

# Sets directory to load .csv file
setwd("D:/Repositories/hadley-cell/R Code/Data")							

# Reads csv/txt file with "null" values ifentified as missing data
data <- read.csv("test.txt", header=FALSE, na.strings=c("null"))	

# Insures data is read numerically and is not a list object
data <- as.numeric(unlist(data))							

# Defines a matrix m that isolates month vectors
m <- matrix(data, ncol = 12, byrow = T)					

# Removes blanks from data series
data <- data[!is.na(data)]

# Runs trend analyses
mk.test(data)										
sens.slope(data)
pettitt.test(data)

# Isolates month vectors
jan <- m[ ,1]
feb <- m[ ,2]
mar <- m[ ,3]
apr <- m[ ,4]
may <- m[ ,5]
jun <- m[ ,6]
jul <- m[ ,7]
aug <- m[ ,8]
sep <- m[ ,9]
oct <- m[ ,10]
nov <- m[ ,11]
dec <- m[ ,12]

# Removes missing values so analyses can be conducted
jan <- jan[!is.na(jan)]	
feb <- feb[!is.na(feb)]
mar <- mar[!is.na(mar)]
apr <- apr[!is.na(apr)]
may <- may[!is.na(may)]
jun <- jun[!is.na(jun)]
jul <- jul[!is.na(jul)]
aug <- aug[!is.na(aug)]
sep <- sep[!is.na(sep)]
oct <- oct[!is.na(oct)]
nov <- nov[!is.na(nov)]
dec <- dec[!is.na(dec)]

# Defines month vectors as time series
jan <- ts(jan)
feb <- ts(feb)
mar <- ts(mar)
apr <- ts(apr)
may <- ts(may)
jun <- ts(jun)
jul <- ts(jul)
aug <- ts(aug)
sep <- ts(sep)
oct <- ts(oct)
nov <- ts(nov)
dec <- ts(dec)

# Begins trend analyses for months
# Trend test statistics are extracted and sorted into vectors
m1 <- sens.slope(jan)
m2 <- sens.slope(feb)
m3 <- sens.slope(mar)
m4 <- sens.slope(apr)
m5 <- sens.slope(may)
m6 <- sens.slope(jun)
m7 <- sens.slope(jul)
m8 <- sens.slope(aug)
m9 <- sens.slope(sep)
m10 <- sens.slope(oct)
m11 <- sens.slope(nov)
m12 <- sens.slope(dec)

# Defines vector of sen slopes for each month series
slopes <- c(m1$b.sen, m2$b.sen,	m3$b.sen, m4$b.sen, m5$b.sen, m6$b.sen, m7$b.sen, m8$b.sen, m9$b.sen, m10$b.sen, m11$b.sen, m12$b.sen)

# Defines vector of intercepts for each month series
int <- c(m1$intercept, m2$intercept, m3$intercept, m4$intercept, m5$intercept, m6$intercept, m7$intercept, m8$intercept, m9$intercept, m10$intercept, m11$intercept, m12$intercept)
nor <- c(m1$nobs, m2$nobs, m3$nobs, m4$nobs, m5$nobs,m6$nobs, m7$nobs, m8$nobs, m9$nobs, m10$nobs, m11$nobs, m12$nobs)

# Run M-K tests
mk1 <- mk.test(jan)
mk2 <- mk.test(feb)
mk3 <- mk.test(mar)
mk4 <- mk.test(apr)
mk5 <- mk.test(may)
mk6 <- mk.test(jun)
mk7 <- mk.test(jul)
mk8 <- mk.test(aug)
mk9 <- mk.test(sep)
mk10 <- mk.test(oct)
mk11 <- mk.test(nov)
mk12 <- mk.test(dec)

# Defines vectors for M-K test statistics
S <- c(mk1$estimates, mk2$estimates, mk3$estimates, mk4$estimates, mk5$estimates, mk6$estimates, mk7$estimates, mk8$estimates, mk9$estimates, mk10$estimates, mk11$estimates, mk12$estimates)
varSg <- c(mk1$varSg, mk2$varSg, mk3$varSg, mk4$varSg, mk5$varSg, mk6$varSg, mk7$varSg, mk8$varSg, mk9$varSg, mk10$varSg, mk11$varSg, mk12$varSg)
Zg <- c(mk1$Zg, mk2$Zg, mk3$Zg, mk4$Zg, mk5$Zg, mk6$Zg, mk7$Zg, mk8$Zg, mk9$Zg, mk10$Zg, mk11$Zg, mk12$Zg)
pvalg <- c(mk1$pvalg, mk2$pvalg, mk3$pvalg, mk4$pvalg, mk5$pvalg, mk6$pvalg, mk7$pvalg, mk8$pvalg, mk9$pvalg, mk10$pvalg, mk11$pvalg, mk12$pvalg)

# Transposes vectors for easy copying
S <- t(S)											
varSg <- t(varSg)
Zg <- t(Zg)
pvalg <- t(pvalg)

# Prints vectors
print(S)
print(varSg)
print(Zg)
print(pvalg)
print(slopes)
print(int)
