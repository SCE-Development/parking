# Use an official Node runtime
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package.json and lock file (package-lock.json or yarn.lock)
COPY package*.json ./

# Install dependencies
# If you use yarn, replace `npm install` with `yarn install`
RUN npm install

# Copy the rest of your app's source code from host to container
COPY . .

# Expose the port the app runs on (Vite default is 5173)
EXPOSE 5173

# Command to run the Vite development server
# The --host flag is important to make the server accessible outside the container
CMD ["npm", "run", "dev", "--", "--host"] 