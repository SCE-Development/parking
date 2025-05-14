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

  const getEarliestQueryDate = () => {
    let d = new Date()
    if(timeRange === "Day") {
      d.setHours(0, 0, 0)
    }
    else if (timeRange == "Week") {
      d = new Date(d.setDate(d.getDate() - d.getDay()))
      d.setHours(0, 0, 0)
    }
    else if(timeRange === "Month"){
      d.setDate(1)
      d.setHours(0, 0, 0)
    }
    else if(timeRange === "Year"){
      d.setMonth(0)
      d.setDate(1)
      d.setHours(0, 0, 0)
    }
    else if(timeRange === "5Year"){
      d.setFullYear(d.getFullYear() - 5)
      d.setMonth(0)
      d.setDate(1)
      d.setHours(0, 0, 0)
    }
    return d
  }

  /* updates garage data to display */
  useEffect(() => {
    setChartData([])

    // convert to date/time format accepted by SQL
    const dateToSQLTimestamp = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0'); // JS months are 0-based
      const day = String(date.getDate()).padStart(2, '0');
    
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
    
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }

    const getData = async () => {
      const updatedChartData = [] //holds new data for all four garage graphs
      /*
      1. (done) fetch all using Promise.all
      2. (done) find earliest a timestamp for to include filtering
        and format date - using ISO
      3. (done) format returned data to be displayed
      */
      // earliest date of data to include in query
      const d = getEarliestQueryDate()
      // console.log(dateToSQLTimestamp(d))

      const p1 = fetch(`/api/parking-history?garage_name=${"North_Garage"}&time_stamp=${dateToSQLTimestamp(d)}`)
      const p2 = fetch(`/api/parking-history?garage_name=${"South_Garage"}&time_stamp=${dateToSQLTimestamp(d)}`)
      const p3 = fetch(`/api/parking-history?garage_name=${"West_Garage"}&time_stamp=${dateToSQLTimestamp(d)}`)
      const p4 = fetch(`/api/parking-history?garage_name=${"South_Campus_Garage"}&time_stamp=${dateToSQLTimestamp(d)}`)

      const rawData = await Promise.all([
        p1, 
        p2, 
        p3, 
        p4])

      const garageData = await Promise.all([
        rawData[0].json(),
        rawData[1].json(),
        rawData[2].json(),
        rawData[3].json()
      ])

      for(const index1 in garageData) {
        const newGarageData = []
        const data = garageData[index1]
        for(let index2 in data) {
          const entry = data[index2]
          const datetime = entry[3].split("T")
          const fullness = entry[2].split(" ")[0].split("%")[0]
      
          const gmtDate = new Date(data[index2][3] + "Z")
          const pacificTime = gmtDate.toLocaleString("en-US", {
              timeZone: "America/Los_Angeles",
          });
      
          const time = pacificTime.split(" ")[1].substring(0, 4)// + pacificTime.split(" ")[2]
          
          const date = pacificTime.split(",")[0].split("/")
          
          const year = date[2]
          const month = date[0].padStart(2, "0")
          const day = date[1].padStart(2, "0")

          const pacificDate = new Date()
          pacificDate.setFullYear(year)
          pacificDate.setMonth(month - 1)
          pacificDate.setDate(day)
          // const pacificDate = new Date("2022-03-25");
          console.log(pacificDate)
          const dayOfWeek = pacificDate.getDay()

          if(timeRange === "Day") {
            newGarageData.unshift({time: time, fullness: fullness})
          }
          else if (timeRange == "Week") {          
            newGarageData.unshift({time: `${numToDayOfWeek[dayOfWeek]}`, fullness: fullness})
          }
          else if(timeRange === "Month"){
            newGarageData.unshift({time: `${month}-${day}`, fullness: fullness})
          }
          else if(timeRange === "Year"){
            newGarageData.unshift({time: numToMonth[month], fullness: fullness})
          }
          else if(timeRange === "5Year"){
            newGarageData.unshift({time: year, fullness: fullness})
          }
        }
        updatedChartData.push(newGarageData)
      }
      setChartData(updatedChartData)
    }
    getData()
  }, [timeRange])

  // console.log(chartData)

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

