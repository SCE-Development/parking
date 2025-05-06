import React, { useState, useEffect } from 'react'
import "./App.css"

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer } from "@/components/ui/chart"
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

//labels, colors for chart
const chartConfig = {
  fullness: {
    label: "Fullness (%)",
    color: "#FF1E57",
  },
}

const App = () => {
  const [timeRange, setTimeRange] = useState("Day")
  const [chartData, setChartData] = useState([])

  const numToMonth = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "Aug",
    "09": "Sept",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec"
  }

  const numToDayOfWeek = {
    "0": "Sun",
    "1": "Mon",
    "2": "Tues",
    "3": "Wed",
    "4": "Thurs",
    "5": "Fri",
    "6": "Sat"
  }
  
  const handleTimeRangeChange = (e) => {
    setTimeRange(e)
  }
  
  const GARAGE_NAMES = ["North_Garage", "South_Garage", "West_Garage", "South_Campus_Garage"]

  /*
    get data for selected garage, get current date,
    only add entries that are in current day, week, or month
  */
  useEffect(() => {
    setChartData([])
    const getData = async () => {

      const updatedChartData = [] //holds new data for all four garage graphs

      for(const index in GARAGE_NAMES) {
        const response = await fetch(`/api/parking-history?garage_name=${GARAGE_NAMES[index]}`)
        const data = await response.json()

        // console.log(data)

        if(data[0] !== undefined) {

          let d = new Date()
          const dateToday = [d.getFullYear(), d.getMonth() + 1, d.getDate()]
          // month ranges from 0-11
          // const dateToday = data[0][3].split("T")[0].split("-")
          // console.log(dateToday)
          // dateToday holds date in format: [year, month, date]

          var newGarageData = []
          for(let index in data) {
            const entry = data[index] 
            const datetime = entry[3].split("T")

            const date = datetime[0].split("-")

            const gmtDate = new Date(data[index][3] + "Z")
            const pacificTime = gmtDate.toLocaleString("en-US", {
              timeZone: "America/Los_Angeles",
            });

            const time = pacificTime.split(" ")[1].substring(0, 4)// + pacificTime.split(" ")[2]
            
            const year = date[0]
            const month = date[1]
            const day = date[2]

            const fullness = entry[2].split(" ")[0].split("%")[0]

            if(timeRange === "Day") {
              console.log(day + ", " + dateToday)
              if(day === dateToday[2] && year == dateToday[0] && month == dateToday[1]) {
                newGarageData.unshift({time: time, fullness: fullness})
              }
            }

            else if (timeRange == "Week") {

              function isDateInThisWeek(date) {
                // issue: should compare only day, month, and year -> don't compare time
                const today = new Date();

                const firstDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay()));
                firstDayOfWeek.setHours(0, 0, 0)
                const lastDayOfWeek = new Date(today.setDate(today.getDate() + 6));
                lastDayOfWeek.setHours(23, 59, 59)

                console.log(date + ", " + firstDayOfWeek + ", " + lastDayOfWeek)
                return date >= firstDayOfWeek && date <= lastDayOfWeek;
              }
              
              const pacificDate = new Date(pacificTime)
              const isInWeek = isDateInThisWeek(pacificDate);

              if (isInWeek) {
                newGarageData.unshift({time: `${numToDayOfWeek[pacificDate.getDay()]}`, fullness: fullness})
                // Sunday - Saturday : 0 - 6
              }
            }

            else if(timeRange === "Month"){
              console.log(month + ", " + dateToday)
              if(month === dateToday[1] && year == dateToday[0]) {
                newGarageData.unshift({time: `${month}-${day}`, fullness: fullness})
              }
            }

            else if(timeRange === "Year"){
              // console.log(year + ", " + dateToday)
              if(year === dateToday[0]) {
                newGarageData.unshift({time: numToMonth[month], fullness: fullness})
              }
            }

            else if(timeRange === "5Year"){
              // console.log(year + ", " + dateToday)
              if(year > dateToday[0] - 5) {
                newGarageData.unshift({time: numToMonth[month], fullness: fullness})
              }
            }

          }
        }
        updatedChartData.push(newGarageData)
      }
      setChartData(updatedChartData)
    }
    getData()
  }, [timeRange])
  // make time a dependency

  console.log(chartData)

  return (
    <>
      <div className="top-nav-div">
        <div className="logo-div">
          <h2 id="logo-text">P</h2>
        </div>
        <h2 id="logo">SCE Parking</h2>
      </div>
      <div className="main-div">
        <div className="options-div">
          <h1>Garage Fullness</h1>
          <br></br>
          <div className="flex flex-row">
            <Select onValueChange={handleTimeRangeChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Today" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Day">Today</SelectItem>
                <SelectItem value="Week">This Week</SelectItem>
                <SelectItem value="Month">This Month</SelectItem>
                <SelectItem value="Year">This Year</SelectItem>
                <SelectItem value="5Year">Past 5 Years</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <br></br>
          <div className="garage-charts-div">
          {chartData.length == 0 ?
          (<h1>Loading...</h1>)
          :
          (<>
            {chartData.map((garageData, index) => (
              <div className="garage-chart" key={index}>
                <div className="garage-name-div">
                  <h2>{GARAGE_NAMES[index].replaceAll("_", " ")}</h2>
                </div>
                <div className="chart-div">
                <br></br>
                  <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
                    <AreaChart
                      accessibilityLayer
                      data={garageData}
                      margin={{
                        left: 12,
                        right: 12,
                      }}
                    >
                      <CartesianGrid vertical={false} />
                      <XAxis
                        dataKey="time"
                        tickLine={false}
                        tickMargin={10}
                        axisLine={false}
                        tickFormatter={(value) => value.slice(0, 5)}
                      />
                      <YAxis
                        dataKey="fullness"
                        tickLine={false}
                        tickMargin={10}
                        axisLine={false}
                        domain={[0, 100]}
                        // tickFormatter={(value) => value.slice(0, 5)}
                      />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <ChartLegend content={<ChartLegendContent />} />

                      <Area
                          dataKey="fullness"
                          type="natural"
                          fill={chartConfig.fullness.color}
                          fillOpacity={0.4}
                          stroke={chartConfig.fullness.color}
                          stackId="a"
                      />
                    </AreaChart>  
                  </ChartContainer>   
                </div>
              </div>  
             ))}
           </>)}
          </div>
        </div>
      </div>
    </>
  )
}

export default App

