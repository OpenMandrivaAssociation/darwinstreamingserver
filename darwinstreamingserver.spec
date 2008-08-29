%define oname	DarwinStreamingSrvr

Summary:	Apple's Darwin Streaming Server
Name:		darwinstreamingserver
Version:	6.0.3
Release:	%{mkrel 1}
License:	APSL 2.0
Group:		System/Servers
URL:		http://developer.apple.com/opensource/server/streaming/index.html
# Upstream download is uncompressed, compress manually - AdamW 2008/08
Source0:	http://dss.macosforge.org/downloads/%{oname}%{version}-Source.tar.lzma
Source1:	dss.init.bz2
Source2:	dss-proxy.init.bz2
Source5:	dss.bz2
Source6:	dss-proxy.bz2
Patch0:		DSS-v6_0_3-Config.diff
# Via http://dss.macosforge.org/trac/ticket/6
# Location http://www.abrahamsson.com/dss-6.0.3.patch
# Fixes various bugs and build errors for Linux, also fixes build for
# x86-64. Author Sverker Abrahamsson.
Patch1:		dss-6.0.3.patch
# Also via http://dss.macosforge.org/trac/ticket/6
# Fixes more minor compilation issues, memory leaks, deadlock, and
# bug on x86-64 preventing any requests from outside localhost. Author
# Horace Hsieh.
Patch2:		dss-hh-20080728-1.patch
Patch3:		darwinstreamingserver-6.0.3-build_optimizer.patch
BuildRequires:	libstdc++-devel
BuildRoot:	%{_tmppath}/%{name}-buildroot
Requires(pre,post,preun,postun):	rpm-helper

%description
Darwin Streaming Server lets you stream digital video on the
Internet using industry-standard Internet protocols RTP and RTSP.

Using Darwin Streaming Server you can serve stored files (video
on demand) or reflect live broadcasts to thousands of QuickTime
4 or later users. With its combination of industry-standard
streaming protocols and cutting-edge compression technologies,
QuickTime delivers perfectly synchronized audio and video streams
ideal for Internet video and live events.

%package	proxy
Summary:	Apple's Darwin Streaming Proxy
Group:		System/Servers
License:	APSL 2.0
Requires(post,preun):		rpm-helper

%description	proxy
The Darwin Streaming Proxy is an application specific proxy which
would normally be run in a border zone or perimeter network. It
is used to give client machines within a protected network access
to streaming servers outside that network, in the case when the
firewall blocks RTSP connections or RTP/UDP data flow. The
firewall perimeter network is usually configured to allow:

* RTSP connections from within the network, as long as the
  destination is the proxy

* RTSP connections to outside the network, as long as the source
  is the proxy

* RTP datagrams to and from the proxy to the inner network

* RTP datagrams to and from the proxy to the outside

%package	utils
Summary:	Apple's Darwin Streaming Server Movie inspection utilities
Group:		System/Servers
License:	APSL 2.0

%description	utils
* QTBroadcaster
  Requires a target ip address, a source movie, one or more source
  hint track ids in movie, and an initial port. Every packet
  referenced by the hint track(s) is broadcasted to the specified
  ip address.

* QTFileInfo
  Requires a movie name. Displays each track id, name, create date,
  and mod date. If the track is a hint track, additional
  information is displayed: the total rtp bytes and packets, the
  average bit rate and packet size, and the total header
  percentage of the stream.

* QTFileTest
  Requires a movie name. Parses the Movie Header Atom and displays
  a trace of the output.

* QTRTPFileTest
  Requires a movie and a hint track id in the movie. Displays the
  RTP header (TransmitTime, Cookie, SeqNum, and TimeStamp) for
  each packet.

* QTRTPGen
  Requires a movie and a hint track id. Displays the number of
  packets in each hint track sample and writes the RTP packets to
  file "track.cache"

* QTSampleLister
  Requires a movie and a track id. Displays track media sample
  number, media time, Data offset, and sample size for each sample
  in the track.

* QTSDPGen
  Requires a list of 1 or more movies. Displays the SDP
  information for all of the hinted tracks in each movie. Use -f
  to save the SDP information to the file [movie].sdp in the same
  directory as the source movie.

* QTTrackInfo
  Requires a movie, sample table atom type, and track id. Displays
  the information in the sample table atom of the specified track.
  Supports "stco", "stsc", "stsz", "stts" as the atom type.

  Example: "./QTTrackInfo -T stco /movies/mystery.mov 3" dumps the
  chunk offset sample table in track 3.

%prep

%setup -q -n %{oname}%{version}-Source
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

cat > defaultPaths.h << EOF
# define DEFAULTPATHS_DIRECTORY_SEPARATOR	"/"
# define DEFAULTPATHS_ETC_DIR			"%{_sysconfdir}/dss/"
# define DEFAULTPATHS_ETC_DIR_OLD		"%{_sysconfdir}/"
# define DEFAULTPATHS_SSM_DIR			"%{_libdir}/dss/"
# define DEFAULTPATHS_LOG_DIR			"/var/log/dss/"
# define DEFAULTPATHS_MOVIES_DIR        "%{_localstatedir}/lib/dss/"
# define DEFAULTPATHS_PID_DIR           "/var/run/dss/"
EOF

%build
export RPM_OPT_FLAGS="%{optflags} -Wall"
export ARCH="%{_target_cpu}"
# parallel build hack... (it sucks)
# export JOBS=$(echo %{_smp_mflags}|cut -dj -f2)
# ./Buildit --jobs=$JOBS
./Buildit

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_sysconfdir}/dss
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_libdir}/dss
install -d %{buildroot}%{_localstatedir}/lib/dss/Movies/http
install -d %{buildroot}%{_localstatedir}/lib/dss/AdminHtml
install -d %{buildroot}%{_localstatedir}/lib/dss/Playlists
install -d %{buildroot}/var/log/dss
install -d %{buildroot}%{_iconsdir}
install -d %{buildroot}%{_miconsdir}
install -d %{buildroot}%{_liconsdir}
install -d %{buildroot}/var/run/dss
install -d %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_libdir}/%{name}-Admin/scripts

install -m0755 DarwinStreamingServer %{buildroot}%{_sbindir}/
install -m0755 StreamingProxy.tproj/StreamingProxy %{buildroot}%{_sbindir}/
install -m0755 PlaylistBroadcaster.tproj/PlaylistBroadcaster %{buildroot}%{_bindir}/
install -m0755 MP3Broadcaster/MP3Broadcaster %{buildroot}%{_bindir}/
install -m0755 qtpasswd.tproj/qtpasswd %{buildroot}%{_bindir}/

# NOTE! the StreamingLoadTool is not yet released as source code
#install -m755 StreamingLoadTool %{buildroot}%{_bindir}/

# modules
install -m0755 APIModules/QTSSDemoAuthorizationModule.bproj/QTSSDemoAuthorizationModule %{buildroot}%{_libdir}/dss/
install -m0755 APIModules/QTSSRawFileModule.bproj/QTSSRawFileModule %{buildroot}%{_libdir}/dss/
install -m0755 APIModules/QTSSRefMovieModule/QTSSRefMovieModule %{buildroot}%{_libdir}/dss/
install -m0755 APIModules/QTSSSpamDefenseModule.bproj/QTSSSpamDefenseModule %{buildroot}%{_libdir}/dss/

# utils
install -m0755 QTFileTools/QTBroadcaster.tproj/QTBroadcaster %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTFileInfo.tproj/QTFileInfo %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTFileTest.tproj/QTFileTest %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTRTPFileTest.tproj/QTRTPFileTest %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTRTPGen.tproj/QTRTPGen %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTSampleLister.tproj/QTSampleLister %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTSDPGen.tproj/QTSDPGen %{buildroot}%{_bindir}/
install -m0755 QTFileTools/QTTrackInfo.tproj/QTTrackInfo %{buildroot}%{_bindir}/

# config
install -m0644 streamingserver.xml %{buildroot}%{_sysconfdir}/dss/
install -m0644 streamingserver.xml %{buildroot}%{_sysconfdir}/dss/streamingserver.xml.default
install -m0644 relayconfig.xml-Sample %{buildroot}%{_sysconfdir}/dss/relayconfig.xml
install -m0644 relayconfig.xml-Sample %{buildroot}%{_sysconfdir}/dss/relayconfig.xml.default
install -m0644 StreamingProxy.tproj/streamingproxy.conf %{buildroot}%{_sysconfdir}/dss/
install -m0644 StreamingProxy.tproj/streamingproxy.conf %{buildroot}%{_sysconfdir}/dss/streamingproxy.conf.default
install -m0644 qtaccess %{buildroot}%{_sysconfdir}/dss/
install -m0644 qtusers %{buildroot}%{_sysconfdir}/dss/
install -m0644 qtgroups %{buildroot}%{_sysconfdir}/dss/

# install manuals
install -m0644 Documentation/broadcasterctl.1 %{buildroot}%{_mandir}/man1/
install -m0644 Documentation/MP3Broadcaster.1 %{buildroot}%{_mandir}/man1/

# NOTE! the StreamingLoadTool is not yet released as source code
#install -m644 streamingloadtool.conf %{buildroot}%{_sysconfdir}/dss/streamingloadtool.conf

# sys 5 scripts
bzcat %{SOURCE1} > %{buildroot}%{_initrddir}/%{name}
bzcat %{SOURCE2} > %{buildroot}%{_initrddir}/%{name}-Proxy

# logrotate stuff
bzcat %{SOURCE5} > %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
bzcat %{SOURCE6} > %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-Proxy

# i strongly suspect the web admin can't follow symlinks..., if
# so, some coder needs to fix the source. As the server is run
# under the dss user, there might be some problems...

ln -s %{_docdir}/%{name}-%{version} %{buildroot}%{_localstatedir}/lib/dss/Docs
ln -s ../../../etc/dss %{buildroot}%{_localstatedir}/lib/dss/Config
ln -s ../../../usr/lib/dss %{buildroot}%{_localstatedir}/lib/dss/Modules
ln -s ../../log/dss %{buildroot}%{_localstatedir}/lib/dss/Logs

# provide ghost logs...
touch %{buildroot}/var/log/dss/Error.log
touch %{buildroot}/var/log/dss/StreamingServer.log
touch %{buildroot}/var/log/dss/mp3_access.log
touch %{buildroot}/var/log/dss/server_status
touch %{buildroot}/var/log/dss/StreamingProxy.log

# strip the modules
strip %{buildroot}%{_libdir}/dss/*

%pre
%_pre_useradd dss %{_localstatedir}/lib/dss /bin/sh

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
%_postun_userdel dss

%post proxy
%_post_service %{name}-Proxy

%preun proxy
%_preun_service %{name}-Proxy

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-, root, root)
%doc APPLE_LICENSE ReleaseNotes.txt
%doc APIModules/QTSSRawFileModule.bproj/README-RawFileModule
%doc APIModules/QTSSRawFileModule.bproj/sampleredirect.raw
%doc Documentation/3rdPartyAcknowledgements.rtf
%doc Documentation/AboutTheSource.html
%doc Documentation/admin-protocol-README.txt
%doc Documentation/CachingProxyProtocol-README.txt
%doc Documentation/DevNotes.html
%doc Documentation/draft-serenyi-avt-rtp-meta-00.txt
%doc Documentation/DSS_QT_Logo_License.pdf
%doc Documentation/License.rtf
%doc Documentation/QTSSAPIDocs.pdf
%doc Documentation/ReadMe.rtf
%doc Documentation/readme.txt
%doc Documentation/ReliableRTP_WhitePaper.rtf
%doc Documentation/RTSP_Over_HTTP.pdf
%doc Documentation/FAQ.html
%attr(0755,root,root) %{_initrddir}/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/qtaccess
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/qtgroups
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/qtusers
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/relayconfig.xml
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/relayconfig.xml.default
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/streamingserver.xml
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/streamingserver.xml.default
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}
%dir %attr(0755, root, root) %{_bindir}/MP3Broadcaster
%dir %attr(0755, root, root) %{_bindir}/PlaylistBroadcaster
%dir %attr(0755, root, root) %{_bindir}/qtpasswd
%dir %attr(0755, root, root) %{_sbindir}/DarwinStreamingServer
%dir %attr(0755, root, root) %{_libdir}/dss
%dir %attr(0755, dss, dss) /var/run/dss
%attr(0755,root,root) %{_libdir}/dss/QTSSDemoAuthorizationModule
%attr(0755,root,root) %{_libdir}/dss/QTSSRawFileModule
%attr(0755,root,root) %{_libdir}/dss/QTSSRefMovieModule
%attr(0755,root,root) %{_libdir}/dss/QTSSSpamDefenseModule
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Movies
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Movies/http
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Playlists
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Docs
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Config
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Modules
%dir %attr(0755, dss, dss) %{_localstatedir}/lib/dss/Logs
%dir %attr(0755, dss, dss) /var/log/dss
%attr(0644,dss,dss) %verify(not md5 size mtime) %ghost /var/log/dss/Error.log
%attr(0644,dss,dss) %verify(not md5 size mtime) %ghost /var/log/dss/StreamingServer.log
%attr(0644,dss,dss) %verify(not md5 size mtime) %ghost /var/log/dss/mp3_access.log
%attr(0644,dss,dss) %verify(not md5 size mtime) %ghost /var/log/dss/server_status
%attr(0644,root,root) %{_mandir}/man1/broadcasterctl.1*
%attr(0644,root,root) %{_mandir}/man1/MP3Broadcaster.1*

%files proxy
%defattr(-, root, root)
%doc APPLE_LICENSE Documentation/CachingProxyProtocol-README.txt
%doc StreamingProxy.tproj/StreamingProxy.html
%attr(0755, root, root) %{_initrddir}/%{name}-Proxy
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/streamingproxy.conf
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dss/streamingproxy.conf.default
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}-Proxy
%dir %attr(0755, root, root) %{_sbindir}/StreamingProxy
%dir %attr(0755, root, root) %{_localstatedir}/lib/dss/Config
%dir %attr(0755, dss, dss) %{_localstatedir}/lib/dss/Logs
%dir %attr(0755, dss, dss) /var/log/dss
%attr(0644,dss,dss) %verify(not md5 size mtime) %ghost /var/log/dss/StreamingProxy.log

%files utils
%defattr(-, root, root)
%doc APPLE_LICENSE Documentation/AboutQTFileTools.html
%dir %attr(0755, root, root) %{_bindir}/QTBroadcaster
%dir %attr(0755, root, root) %{_bindir}/QTFileInfo
%dir %attr(0755, root, root) %{_bindir}/QTFileTest
%dir %attr(0755, root, root) %{_bindir}/QTRTPFileTest
%dir %attr(0755, root, root) %{_bindir}/QTRTPGen
%dir %attr(0755, root, root) %{_bindir}/QTSampleLister
%dir %attr(0755, root, root) %{_bindir}/QTSDPGen
%dir %attr(0755, root, root) %{_bindir}/QTTrackInfo

