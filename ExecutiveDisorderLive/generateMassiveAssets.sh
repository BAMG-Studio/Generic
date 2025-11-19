#!/bin/bash

# Create comprehensive folder structure for 100+ cards
echo "Creating card folder structure for 100 cards..."
cd Dropbox/Replit/Art/Cards
mkdir -p EDX_Series

# Create 100 card folders
for i in $(seq 1 100); do
  cardnum=$(printf "EDX%d" $i)
  mkdir -p "EDX_Series/$cardnum"
  mkdir -p "EDX_Series/$cardnum/thumbnails"
  mkdir -p "EDX_Series/$cardnum/icons"
done

echo "Created $(ls -1 EDX_Series | wc -l) card folders"

# Create crisis asset folders
cd ../../
mkdir -p Crisis/{Protesters,Whistleblowers,Rivals,Activists,Journalists,Hackers,Spies,Rebels,Extremists,Infiltrators}

# Create logo variations folder
mkdir -p Brand/Logos/variations

# Create portrait subfolders
mkdir -p Portraits/{Executives,Staff,Stakeholders,Crisis,Citizens,International}

# Create more scene folders
mkdir -p Scenes/{Backgrounds,CrisisScenes,NewsScenes,MeetingRooms,PublicSpaces}

echo "Complete folder structure created!"
cd ~/

ls -la Dropbox/Replit/Art/Cards/EDX_Series | head -20
