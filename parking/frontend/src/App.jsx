import React, { useState, useEffect } from 'react'
import Color_Test from "./Color_test.jsx"

import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"
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
    color: "#60a5fa",
  },
}

const App = () => {
  const [garage, setGarage] = useState("")
  const [timeRange, setTimeRange] = useState("Day")
  const [chartData, setChartData] = useState([])

  const numToMonth = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
  }

  const handleGarageChange = (e) => {
    setGarage(e)
  }
  
  const handleTimeRangeChange = (e) => {
    setTimeRange(e)
  }
  
  /*
    get data for selected garage, get current date,
    only add entries that are in current day, week, or month
  */
  useEffect(() => {
    const getData = async () => {
      const response = await fetch(`http://localhost:8000/parking-history?garage_name=${garage}`)
      const data = await response.json()

      if(data[0] !== undefined) {
        const dateToday = data[0][3].split("T")[0].split("-")
        // dateToday holds date in format: [year, month, date]

        var newChartData = []
        for(let index in data) {
          const entry = data[index] 
          const datetime = entry[3].split("T")
          console.log(datetime[0])
          const date = datetime[0].split("-")

          const time = datetime[1]
          
          const year = date[0]
          const month = date[1]
          const day = date[2]

          const fullness = entry[2].split(" ")[0].split("%")[0]
          if(timeRange === "Day") {
            if(day === dateToday[2]) {
              newChartData.unshift({time: time, fullness: fullness})
            }
          }
          else if(timeRange === "Month"){
            if(month === dateToday[1]) {
              newChartData.unshift({time: `${month}-${day}`, fullness: fullness})
            }
          }
          else if(timeRange === "Year"){
            if(year === dateToday[0]) {
              newChartData.unshift({time: numToMonth[month], fullness: fullness})
            }
          }
        }
      }
      setChartData(newChartData)
    }
    getData()
  }, [garage, timeRange])
  // make garage and time dependencies

  return (
    <>
      <h1>Garage Fullness</h1>
      <br></br>
      <div className="flex flex-row">
        <Select onValueChange={handleGarageChange}>
          <SelectTrigger className="w-[230px]">
            <SelectValue placeholder="Select Garage" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="South_Garage">South Garage</SelectItem>
            <SelectItem value="North_Garage">North Garage</SelectItem>
            <SelectItem value="West_Garage">West Garage</SelectItem>
            <SelectItem value="South_Campus_Garage">South Campus Garage</SelectItem>
          </SelectContent>
        </Select>
        <Select onValueChange={handleTimeRangeChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Today" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Day">Today</SelectItem>
            <SelectItem value="Month">This Month</SelectItem>
            <SelectItem value="Year">This Year</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <br></br>
      <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
        <AreaChart
          accessibilityLayer
          data={chartData}
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
    </>
  )
}

export default App

