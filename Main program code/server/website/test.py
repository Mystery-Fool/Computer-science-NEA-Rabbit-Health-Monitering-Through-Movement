import mysql.connector
import scipy.stats as stats

timefactor=10**6
Connector = mysql.connector.connect(user="root", password="rabbit42!", host="localhost", database="RabbitHealth")
statement = "SELECT Avg_Pet1_Time_Moving, Avg_Pet2_Time_Moving FROM Hourly_Movement ORDER BY Date DESC LIMIT " + str(7 * 24)
Cursor = Connector.cursor()
Cursor.execute(statement)
Average = Cursor.fetchall()
Cursor.close()
cinny, cleo = [], []
for x in range(len(Average)):
    cinny.append(Average[x][0])
    cleo.append(Average[x][1])
total_cinny_p_value=0
total_cleo_p_value=0
counter=0
while True:
    counter+=1
    sum_sq_cinny, sum_sq_cleo = 0, 0
    cinny_mean, cleo_mean = 0, 0
    for iterator in range(len(cinny)):
        cinny_mean += int(cinny[iterator])/timefactor
        sum_sq_cinny += int(cinny[iterator])/timefactor ** 2
        cleo_mean += int(cleo[iterator])/timefactor
        sum_sq_cleo += int(cleo[iterator])/timefactor ** 2
    sq_sum_cinny = cinny_mean ** 2
    sq_sum_cleo = cleo_mean ** 2
    cinny_standard_deviation = (((sum_sq_cinny) - (sq_sum_cinny / len(cinny))) / len(cinny)) ** 0.5
    cleo_standard_deviation = (((sum_sq_cleo) - (sq_sum_cleo / len(cleo))) / len(cleo)) ** 0.5
    cinny_mean=cinny_mean/len(cinny)
    cleo_mean=cleo_mean/len(cleo)
    normal_cinny = stats.norm.rvs(loc=cinny_mean, scale=cinny_standard_deviation, size = 100000)
    normal_cleo = stats.norm.rvs(loc=cleo_mean, scale=cleo_standard_deviation, size = 100000)    
    cinny_mean, cleo_mean = 0, 0
    for iterator in range(0, 24):
        cinny_mean += int(cinny[iterator])/timefactor
        cleo_mean += int(cleo[iterator])/timefactor
    cinny_mean = cinny_mean / 24
    cleo_mean = cleo_mean / 24
    cinny_p_value = stats.ttest_1samp(normal_cinny, cinny_mean)[1]
    cleo_p_value = stats.ttest_1samp(normal_cleo, cleo_mean)[1]
    total_cinny_p_value+=cinny_p_value
    total_cleo_p_value+=cleo_p_value
    if counter==100:
        counter=0
        total_cinny_p_value=total_cinny_p_value/100
        total_cleo_p_value=total_cleo_p_value/100
        print(total_cinny_p_value,"  ", total_cleo_p_value)
        print("test")