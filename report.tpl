<html>
<head>
<title>Mailing List Stats</title>
<script src="sorttable.js"></script>
<style>
table.sortable thead
{
    background-color:#eee;
    color:#666666;
    font-weight: bold;
    cursor: default;
}
th
{
     text-align: left;
}
h3
{
	background-color: lightblue;
}
</style>
</head>
<body>
<h1>'@!heading!@' Mailing List Stats</h1>
<h3>General Statistics</h3>
<table>
<tr><th>Total Mails:</th><td>@!totalmails!@</td></tr>
<tr><th>Total Threads:</th><td>@!totalthreads!@</td></tr>
</table>
<h3>Charts</h3>
<div style="padding: 1em; width: 520px;">
<div style="width: 250px; float: left;"><a href="ml-files/ml-emailsperauthor.png"><img src="ml-files/ml-emailsperauthor.png" alt="Emails Per Author" height=150 width=250></br><center>Emails Per Author</center></a></div>
<div style="width: 250px; float: left;"><a href="ml-files/ml-threadsperauthor.png"><img src="ml-files/ml-threadsperauthor.png" alt="Emails Per Author" height=150 width=250></br><center>Threads Per Author</center></a></div>
<div style="clear: both"></div>
</div>
</br>
<h3>Yearly Usage Charts</h3>
<ul>
<!--(for i in yr)-->
<li><a href="ml-files/ml-usage-@!i!@.png">@!i!@</a></li>
<!--(end)-->
</ul>
<h3>User Statistics</h3>
<table class="sortable">
<tr><th>Name</th><th>Mails Sent</th><th>Threads Started</th><th>Last Message</th></tr>
<!--(for i in sa)-->
<tr>
<td><a href="ml-files/@!mydic[i].pagename!@">@!mydic[i].mail!@</a></td><td>@!mydic[i].posts!@</td><td>@!mydic[i].started!@</td><td sorttable_customkey="@!int(mydic[i].lastmsgdate)!@">@!mydic[i].lastmsgdatestr!@</td>
</tr>
<!--(end)-->
</table>
</body>
</html>
