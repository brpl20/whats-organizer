# zip_analyser.py
import zipfile
import os
import datetime
import time
import sys
import binascii
import struct
import hashlib
import collections
import re

# Maximum size to allow for extracted content (300mb)
MAX_EXTRACTED_SIZE = 0.3 * 1024 * 1024 * 1024
# Max compression ratio to detect ZIP bombs (1:1000)
MAX_COMPRESSION_RATIO = 1000
# Max number of files to allow
MAX_FILES = 2000

def analyze_zip_file(zip_path):
    try:
        # Check if file exists
        if not os.path.exists(zip_path):
            return f"Error: File '{zip_path}' does not exist."
            
        # Check if file is a zip file
        if not zipfile.is_zipfile(zip_path):
            return f"Error: '{zip_path}' is not a valid ZIP file."
        
        # Get file size
        file_size = os.path.getsize(zip_path)
        
        # Get file creation/modification times
        file_stats = os.stat(zip_path)
        creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime)
        modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime)
        access_time = datetime.datetime.fromtimestamp(file_stats.st_atime)
        
        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files
            file_list = zip_ref.namelist()
            
            # Check for ZIP bomb - too many files
            if len(file_list) > MAX_FILES:
                return f"SECURITY ALERT: Potential ZIP bomb detected - contains {len(file_list)} files, which exceeds the maximum allowed ({MAX_FILES})."
            
            # Get comment if any
            comment = zip_ref.comment.decode('utf-8', errors='replace') if zip_ref.comment else None
            
            # Get file info for each file
            file_details = []
            total_compressed_size = 0
            total_uncompressed_size = 0
            
            # Track unique extensions and creation tools
            extensions = set()
            compression_methods_used = set()
            oldest_file_date = datetime.datetime.now()
            newest_file_date = datetime.datetime(1980, 1, 1)
            has_encrypted_files = False
            has_directories = False
            create_systems = set()
            extract_versions = set()
            creator_tools = set()
            common_prefixes = []
            timestamps = []
            
            # Extract common path structures
            path_parts = collections.defaultdict(int)
            path_depths = collections.defaultdict(int)
            username_patterns = []
            
            # Collect WhatsApp conversation file names
            whatsapp_contact_names = []
            
            # ZIP bomb checks
            suspicious_files = []
            
            for file in file_list:
                info = zip_ref.getinfo(file)
                compressed_size = info.compress_size
                uncompressed_size = info.file_size
                compression_method = info.compress_type
                
                # Check for ZIP bomb - single file ratio
                if uncompressed_size > 0 and compressed_size > 0:
                    ratio = uncompressed_size / compressed_size
                    if ratio > MAX_COMPRESSION_RATIO:
                        suspicious_files.append(f"{file} (ratio: {ratio:.1f})")
                
                # Check for ZIP bomb - total size
                total_uncompressed_size += uncompressed_size
                if total_uncompressed_size > MAX_EXTRACTED_SIZE:
                    return f"SECURITY ALERT: Potential ZIP bomb detected - would expand to over {format_size(MAX_EXTRACTED_SIZE)}"
                
                # Extract WhatsApp contact names (specifically for Windows/DOS systems)
                whatsapp_pattern = re.search(r'Conversa do WhatsApp com (.+)\.txt$', file)
                if whatsapp_pattern:
                    whatsapp_contact_names.append(whatsapp_pattern.group(1))
                
                # Get file extension
                _, ext = os.path.splitext(file)
                if ext:
                    extensions.add(ext.lower())
                
                # Convert compression method number to name
                method_name = "Unknown"
                if compression_method == zipfile.ZIP_STORED:
                    method_name = "Stored (no compression)"
                elif compression_method == zipfile.ZIP_DEFLATED:
                    method_name = "Deflated"
                elif compression_method == zipfile.ZIP_BZIP2:
                    method_name = "BZIP2"
                elif compression_method == zipfile.ZIP_LZMA:
                    method_name = "LZMA"
                
                compression_methods_used.add(method_name)
                
                # Calculate compression ratio if applicable
                if uncompressed_size > 0:
                    compression_ratio = (1 - compressed_size / uncompressed_size) * 100
                else:
                    compression_ratio = 0
                
                # Check for encryption
                is_encrypted = (info.flag_bits & 0x1) != 0
                if is_encrypted:
                    has_encrypted_files = True
                
                # Check if directory
                is_dir = file.endswith('/')
                if is_dir:
                    has_directories = True
                
                # Get file date
                modified_date = datetime.datetime(*info.date_time)
                timestamps.append(modified_date)
                
                # Track oldest and newest file
                if modified_date < oldest_file_date:
                    oldest_file_date = modified_date
                if modified_date > newest_file_date:
                    newest_file_date = modified_date
                
                # Get CRC32 checksum
                crc = info.CRC
                
                # Get header offset
                header_offset = info.header_offset
                
                # Get extra fields if any
                extra = info.extra
                
                # Track create system
                create_systems.add(info.create_system)
                
                # Track extract version
                extract_versions.add(info.extract_version)
                
                # Analyze path for username patterns
                path_parts_list = file.split('/')
                for idx, part in enumerate(path_parts_list):
                    path_parts[part] += 1
                    path_depths[idx] += 1
                    
                    # Look for possible username patterns in paths
                    username_pattern = re.search(r'[/\\]Users[/\\]([^/\\]+)[/\\]', file, re.IGNORECASE)
                    if username_pattern and username_pattern.group(1) not in ['Public', 'Shared', 'Default', 'All Users']:
                        username_patterns.append(username_pattern.group(1))
                
                # Look for common prefixes
                if len(path_parts_list) > 1:
                    prefix = path_parts_list[0]
                    if prefix and prefix not in common_prefixes:
                        common_prefixes.append(prefix)
                
                file_details.append({
                    'name': file,
                    'size': uncompressed_size,
                    'compressed_size': compressed_size,
                    'compression_method': method_name,
                    'compression_ratio': compression_ratio,
                    'modified': modified_date,
                    'is_dir': is_dir,
                    'is_encrypted': is_encrypted,
                    'crc': crc,
                    'header_offset': header_offset,
                    'extra': extra,
                    'internal_attr': info.internal_attr,
                    'external_attr': info.external_attr,
                    'create_system': info.create_system,
                    'extract_version': info.extract_version,
                    'flag_bits': info.flag_bits,
                    'volume': info.volume,
                })
                
                total_compressed_size += compressed_size
                
            # Report if suspicious compression ratios found
            if suspicious_files:
                return f"SECURITY ALERT: Potential ZIP bomb detected - {len(suspicious_files)} files with suspicious compression ratios:\n" + "\n".join(suspicious_files)
                
        # Check for embedded comments or strings that might reveal creator
        embedded_creators = extract_embedded_creators(zip_path)
        
        # Check for specific tool signatures
        tool_signatures = detect_creation_tool(zip_path, file_details)
        if tool_signatures:
            creator_tools.update(tool_signatures)
        
        # Check for digital signatures
        signature_info = check_for_signatures(zip_path)
        
        # Perform timestamp analysis
        timestamp_analysis = analyze_timestamps(timestamps)
        
        # Check for file insertion after creation
        insertion_analysis = detect_file_insertion(timestamps, file_details)
        
        # Analyze username patterns
        username_analysis = ""
        if username_patterns:
            unique_usernames = list(set(username_patterns))
            username_analysis = f"Potential usernames found in paths: {', '.join(unique_usernames)}\n"
        
        # Find most common directories/paths
        common_paths = find_common_paths(path_parts)
        
        # Calculate hashes
        md5_hash = calculate_file_hash(zip_path, 'md5')
        sha1_hash = calculate_file_hash(zip_path, 'sha1')
        sha256_hash = calculate_file_hash(zip_path, 'sha256')
        
        # Prepare output
        result = f"ZIP File Analysis: {os.path.basename(zip_path)}\n"
        result += f"Full Path: {os.path.abspath(zip_path)}\n"
        result += f"File Size: {file_size} bytes ({format_size(file_size)})\n"
        result += f"Created: {creation_time}\n"
        result += f"Modified: {modification_time}\n"
        result += f"Last Accessed: {access_time}\n"
        result += f"File Permissions: {oct(file_stats.st_mode)[-3:]}\n"
        result += f"Owner UID: {file_stats.st_uid}\n"
        result += f"Owner GID: {file_stats.st_gid}\n"
        result += f"Number of files: {len(file_list)}\n"
        result += f"Total uncompressed size: {total_uncompressed_size} bytes ({format_size(total_uncompressed_size)})\n"
        result += f"Total compressed size: {total_compressed_size} bytes ({format_size(total_compressed_size)})\n"
        
        if total_uncompressed_size > 0:
            overall_ratio = (1 - total_compressed_size / total_uncompressed_size) * 100
            result += f"Overall compression ratio: {overall_ratio:.2f}%\n"
        
        result += f"Contains directories: {'Yes' if has_directories else 'No'}\n"
        result += f"Contains encrypted files: {'Yes' if has_encrypted_files else 'No'}\n"
        result += f"Oldest file date: {oldest_file_date}\n"
        result += f"Newest file date: {newest_file_date}\n"
        result += f"File extensions found: {', '.join(sorted(extensions)) if extensions else 'None'}\n"
        result += f"Compression methods used: {', '.join(sorted(compression_methods_used))}\n"
        result += f"Creation systems: {', '.join(sorted([get_system_name(sys) for sys in create_systems]))}\n"
        
        # Add hash information
        result += f"MD5 hash: {md5_hash}\n"
        result += f"SHA1 hash: {sha1_hash}\n"
        result += f"SHA256 hash: {sha256_hash}\n"
        
        # Add WhatsApp contacts information (only for Windows/DOS system)
        is_windows_dos = any(sys in [0, 10, 14] for sys in create_systems)
        if whatsapp_contact_names and is_windows_dos:
            result += "\nWhatsApp Contacts Found:\n"
            for name in whatsapp_contact_names:
                result += f"  - {name}\n"
            result += f"Name extraction successful: {len(whatsapp_contact_names) > 0}\n"
        elif not is_windows_dos and any('_chat.txt' in file for file in file_list):
            result += "\nMac format WhatsApp backup detected - skipping name extraction\n"
        
        # Add origin information
        result += "\nOrigin Analysis:\n"
        
        if creator_tools:
            result += f"Detected possible creation tools: {', '.join(creator_tools)}\n"
        
        if embedded_creators:
            result += f"Embedded creator information: {embedded_creators}\n"
        
        if common_prefixes:
            result += f"Common root directories: {', '.join(common_prefixes)}\n"
        
        if common_paths:
            result += f"Common path elements: {', '.join(common_paths)}\n"
        
        if username_analysis:
            result += username_analysis
        
        result += timestamp_analysis
        
        # Add file insertion analysis
        if insertion_analysis:
            result += insertion_analysis
        
        # Add comment information
        if comment:
            result += f"\nArchive comment: {comment}\n"
        
        # Add signature information
        if signature_info:
            result += "\nSignature Information:\n"
            result += signature_info
        else:
            result += "\nNo digital signatures were detected in this ZIP file.\n"
        
        result += "\nDetailed File List:\n"
        for item in file_details:
            prefix = "[DIR] " if item['is_dir'] else ""
            result += f"\n{prefix}{item['name']}\n"
            if not item['is_dir']:
                result += f"  Size: {item['size']} bytes ({format_size(item['size'])})\n"
                result += f"  Compressed: {item['compressed_size']} bytes ({format_size(item['compressed_size'])})\n"
                result += f"  Method: {item['compression_method']}\n"
                result += f"  Compression Ratio: {item['compression_ratio']:.2f}%\n"
                result += f"  Modified: {item['modified']}\n"
                result += f"  CRC-32: {hex(item['crc'])}\n"
                result += f"  Header Offset: {item['header_offset']}\n"
                result += f"  Encrypted: {'Yes' if item['is_encrypted'] else 'No'}\n"
                result += f"  Create System: {get_system_name(item['create_system'])}\n"
                result += f"  Extract Version: {item['extract_version']}\n"
                result += f"  Flag Bits: {bin(item['flag_bits'])}\n"
                result += f"  Volume: {item['volume']}\n"
                
                if item['extra']:
                    result += f"  Extra Fields: {binascii.hexlify(item['extra']).decode('ascii')}\n"
                
                result += f"  Internal Attributes: {bin(item['internal_attr'])}\n"
                result += f"  External Attributes: {bin(item['external_attr'])}\n"
        
        return result
            
    except Exception as e:
        return f"Error analyzing ZIP file: {str(e)}"

def check_for_signatures(zip_path):
    """Check for digital signatures in the ZIP file"""
    try:
        # Open the file in binary mode
        with open(zip_path, 'rb') as f:
            data = f.read()
            
        # Check for standard ZIP signatures
        
        # Check for central directory digital signature (0x05054b50)
        sig_marker = b'PK\x05\x05'
        
        if sig_marker in data:
            pos = data.find(sig_marker)
            signature_info = "Found Central Directory Digital Signature at offset: " + str(pos) + "\n"
            
            # Try to extract signature data
            try:
                # Move past the signature marker
                pos += 4
                
                # Extract the signature size
                sig_size = struct.unpack('<H', data[pos:pos+2])[0]
                pos += 2
                
                # Extract the signature data if available
                if sig_size > 0:
                    signature_data = data[pos:pos+sig_size]
                    signature_info += f"  Signature size: {sig_size} bytes\n"
                    signature_info += f"  Signature data (hex): {binascii.hexlify(signature_data).decode('ascii')}\n"
                    
                    # Check for PKCS#7 signature format
                    if signature_data.startswith(b'\x30'):
                        signature_info += "  Signature appears to be in PKCS#7 or ASN.1 DER format\n"
                        
                        # Look for embedded certificate information
                        cert_data = extract_cert_info(signature_data)
                        if cert_data:
                            signature_info += cert_data
            except:
                signature_info += "  Could not parse signature data structure\n"
                
            return signature_info
            
        # Check for APK Signing Block (Android APK files)
        apk_sig_marker = b'APK Sig Block 42'
        if apk_sig_marker in data:
            return "Found Android APK Signature Block\n"
            
        # Check for Microsoft Office document signatures (if it's a ZIP-based Office file)
        if b'_xmlsignatures' in data:
            return "Found Microsoft Office XML Digital Signature\n"
            
        return None
        
    except Exception as e:
        return f"Error checking for signatures: {str(e)}"

def extract_cert_info(signature_data):
    """Try to extract certificate information from ASN.1 DER encoded signature"""
    try:
        # This is a very simplified ASN.1 parser and will only work for some signatures
        info = ""
        
        # Look for common certificate fields
        # Subject CN field often contains a name
        cn_match = re.search(b'\x06\x03\x55\x04\x03.{1,5}([\x20-\x7E]{3,64})', signature_data)
        if cn_match:
            info += f"  Certificate CN: {cn_match.group(1).decode('ascii', errors='replace')}\n"
        
        # Look for email addresses
        email_match = re.search(br'[\x20-\x7E]{3,64}@[\x20-\x7E]{3,64}\.[a-zA-Z]{2,10}', signature_data)
        if email_match:
            info += f"  Certificate Email: {email_match.group(0).decode('ascii', errors='replace')}\n"
            
        return info
    except:
        return ""

def detect_creation_tool(zip_path, file_details):
    """Detect possible creation tools based on file patterns and metadata"""
    tools = set()
    
    try:
        # Open the file in binary mode for tool signature detection
        with open(zip_path, 'rb') as f:
            data = f.read(10240)  # Read first 10KB to check headers
            
        # Check for specific tool signatures
        if b'WinZip' in data:
            tools.add('WinZip')
        if b'PKZIP' in data:
            tools.add('PKZIP')
        if b'7-Zip' in data:
            tools.add('7-Zip')
        if b'Info-ZIP' in data:
            tools.add('Info-ZIP')
        
        # Check for macOS specific patterns
        macos_patterns = False
        for detail in file_details:
            if '__MACOSX/' in detail['name'] or '.DS_Store' in detail['name']:
                macos_patterns = True
                break
        
        if macos_patterns:
            tools.add('macOS Archive Utility or Finder')
        
        # Check for Windows patterns
        windows_patterns = False
        for detail in file_details:
            if 'Thumbs.db' in detail['name'] or 'Desktop.ini' in detail['name']:
                windows_patterns = True
                break
        
        if windows_patterns:
            tools.add('Windows Explorer or built-in ZIP tool')
            
        # Check for Java JAR patterns
        jar_patterns = False
        for detail in file_details:
            if 'META-INF/MANIFEST.MF' in detail['name']:
                jar_patterns = True
                break
                
        if jar_patterns:
            tools.add('Java JAR tool')
        
        # Check for specific system codes that might indicate creation tool
        systems = {detail['create_system'] for detail in file_details}
        if 0 in systems:  # MS-DOS
            tools.add('MS-DOS/Windows ZIP utility')
        if 3 in systems:  # UNIX
            tools.add('UNIX/Linux ZIP utility')
        if 19 in systems:  # OS X
            tools.add('macOS ZIP utility')
            
        return tools
    except:
        return set()

def extract_embedded_creators(zip_path):
    """Try to extract creator information embedded in the ZIP file"""
    try:
        with open(zip_path, 'rb') as f:
            data = f.read()
            
        creator_info = []
        
        # Look for common creator string patterns
        patterns = [
            (rb'Created by ([A-Za-z0-9\.\- ]{3,30})', 'Creator'),
            (rb'Generated by ([A-Za-z0-9\.\- ]{3,30})', 'Generator'),
            (rb'Author: ([A-Za-z0-9\.\- ]{3,30})', 'Author'),
            (rb'Producer: ([A-Za-z0-9\.\- ]{3,30})', 'Producer')
        ]
        
        for pattern, label in patterns:
            matches = re.findall(pattern, data)
            for match in matches:
                try:
                    creator_info.append(f"{label}: {match.decode('utf-8', errors='replace')}")
                except:
                    pass
        
        return "; ".join(creator_info) if creator_info else None
    except:
        return None

def analyze_timestamps(timestamps):
    """Analyze file timestamp patterns for insights about creation"""
    if not timestamps or len(timestamps) < 2:
        return "Timestamp analysis: Not enough timestamps for analysis\n"
        
    # Sort timestamps
    timestamps.sort()
    
    # Get time ranges
    time_range = timestamps[-1] - timestamps[0]
    
    # Check for timestamp clustering
    clusters = []
    current_cluster = [timestamps[0]]
    
    for i in range(1, len(timestamps)):
        diff = (timestamps[i] - timestamps[i-1]).total_seconds()
        if diff < 300:  # 5 minute window
            current_cluster.append(timestamps[i])
        else:
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
            current_cluster = [timestamps[i]]
    
    if len(current_cluster) > 1:
        clusters.append(current_cluster)
    
    # Check for timezone patterns
    hours = [ts.hour for ts in timestamps]
    hour_counts = collections.Counter(hours)
    
    # Generate analysis
    analysis = "Timestamp analysis:\n"
    analysis += f"  Time span: {time_range}\n"
    
    if time_range.days < 1:
        analysis += "  All files created/modified within a single day\n"
    elif time_range.days < 7:
        analysis += "  All files created/modified within a week\n"
    
    if clusters:
        analysis += f"  Found {len(clusters)} clusters of timestamps (files created/modified together)\n"
        largest_cluster = max(clusters, key=len)
        analysis += f"  Largest cluster: {len(largest_cluster)} files from {largest_cluster[0]} to {largest_cluster[-1]}\n"
    
    # Hour distribution might indicate timezone
    common_hours = [hour for hour, count in hour_counts.most_common(3)]
    analysis += f"  Most common hours for file timestamps: {', '.join(map(str, common_hours))}\n"
    
    # Working hours check
    working_hours_count = sum(hour_counts[h] for h in range(9, 18))
    if working_hours_count > len(timestamps) * 0.7:
        analysis += "  Most files were modified during typical working hours (9am-6pm)\n"
    
    return analysis

def detect_file_insertion(timestamps, file_details):
    """Detect potential file insertions after initial archive creation"""
    if len(timestamps) < 3:
        return None
        
    # Sort timestamps and get info
    timestamp_file_map = {}
    for file in file_details:
        timestamp_file_map[file['modified']] = file['name']
    
    sorted_times = sorted(timestamps)
    time_gaps = []
    
    # Find significant time gaps between files (possible insertion points)
    for i in range(1, len(sorted_times)):
        gap = (sorted_times[i] - sorted_times[i-1]).total_seconds()
        if gap > 86400:  # 1 day gap
            time_gaps.append((sorted_times[i-1], sorted_times[i], gap))
    
    # Check if majority of files were created within a close timeframe with outliers
    main_cluster_end = None
    outliers = []
    
    if time_gaps:
        sorted_gaps = sorted(time_gaps, key=lambda x: x[2], reverse=True)
        largest_gap = sorted_gaps[0]
        
        # Count files before and after the largest gap
        files_before = sum(1 for t in timestamps if t <= largest_gap[0])
        files_after = sum(1 for t in timestamps if t >= largest_gap[1])
        
        # If significant portion of files come after a big gap, might indicate insertion
        if files_before > files_after and files_after / len(timestamps) < 0.3:
            main_cluster_end = largest_gap[0]
            for t in sorted_times:
                if t > main_cluster_end and (t - main_cluster_end).total_seconds() > 86400:
                    outliers.append((t, timestamp_file_map.get(t, "Unknown file")))
    
    if outliers:
        result = "\nSuspicious File Insertion Analysis:\n"
        result += f"  Most files were added before {main_cluster_end}\n"
        result += "  The following files may have been inserted later:\n"
        for date, filename in outliers:
            result += f"    - {filename} (added on {date})\n"
        return result
    
    return None

def find_common_paths(path_parts):
    """Find common path elements that might indicate origin"""
    # Filter to keep only recurring elements (appearing at least twice)
    recurring = [part for part, count in path_parts.items() if count > 1 and len(part) > 2]
    
    # Sort by frequency
    recurring.sort(key=lambda x: path_parts[x], reverse=True)
    
    # Return top items (up to 5)
    return recurring[:5]

def get_system_name(system_code):
    """Convert system code to readable name"""
    systems = {
        0: "MS-DOS and OS/2 (FAT / VFAT / FAT32 file systems)",
        1: "Amiga",
        2: "OpenVMS",
        3: "UNIX",
        4: "VM/CMS",
        5: "Atari ST",
        6: "OS/2 H.P.F.S.",
        7: "Macintosh",
        8: "Z-System",
        9: "CP/M",
        10: "Windows NTFS",
        11: "MVS (OS/390 - Z/OS)",
        12: "VSE",
        13: "Acorn Risc",
        14: "VFAT",
        15: "alternate MVS",
        16: "BeOS",
        17: "Tandem",
        18: "OS/400",
        19: "OS X (Darwin)",
        20: "Windows CE"
    }
    return systems.get(system_code, f"Unknown ({system_code})")

def calculate_file_hash(file_path, hash_type='md5'):
    """Calculate file hash"""
    hash_func = None
    if hash_type.lower() == 'md5':
        hash_func = hashlib.md5()
    elif hash_type.lower() == 'sha1':
        hash_func = hashlib.sha1()
    elif hash_type.lower() == 'sha256':
        hash_func = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")
    
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def format_size(size_in_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python zip_analyzer.py <path_to_zip_file> [output_file]")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    result = analyze_zip_file(zip_path)
    
    # If output file is specified, write to file instead of console
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Analysis written to {output_file}")
    else:
        print(result)