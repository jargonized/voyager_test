import re
import csv

infile='../data/data.txt'
outfile='../data/output.csv'
# Read the data from the file
with open(infile, 'r') as file:
    data = file.readlines()
pattern = r'ts=(\d+)\s+pid=(\d+)\s+inst=(\d+)\s+cpuid=(\d+)\s+rip=([\da-fx]+)\s+va=([\da-fx]+)'

# Prepare the CSV data
csv_data = []
for line in data:
    #match = re.match(r'ts=(\d+) mstress pid=(\d+)  inst=(\d+) cpuid=(\d+) rip=([a-f\d]+) va=([a-f\d]+)', line)
    match = re.match(pattern, line)
    if match:
        ts, pid, inst, cpuid, rip, va = match.groups()
        #csv_data.append([ts, pid, inst, cpuid, rip, '0x'+va])
        #csv_data.append(['0x'+va+":",'R', '0x'+va])
        #csv_data.append([va+":",'R', va])
        # Convert the hexadecimal address to an integer
        addr_int = int(va, 16)

        # Shift the address right by 12 bits
        shifted_addr_int = addr_int >> 12

        # Convert the shifted integer address back to hexadecimal format
        shifted_addr_hex = hex(shifted_addr_int)
        #csv_data.append([ts, pid, inst, cpuid, rip, '0x'+va])
        #Format Unique Instr Id, Cycle Count, Load Address, Instruction Pointer of the Load, LLC hit/miss
        #sample 4, 15, 28e837c88340, 406a82, 0
        modified_shifted_addr_hex = shifted_addr_hex.replace('0x', '')
        csv_data.append([4, 15, modified_shifted_addr_hex, 406a82, 0])


# Write CSV data to a file
with open(outfile, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile,delimiter=",")
    #csv_writer.writerow(['ts', 'pid', 'inst', 'cpuid', 'rip', 'va'])
    csv_writer.writerows(csv_data)

print("CSV conversion completed.")
