<html>

<head>
	<title>Quick SLPK Server</title>
</head>

<body>
	<b>List of available services:</b>
	<ul>
		% for folder in folders:
		<li><a href="{{folder[0]}}/{{folder[1]}}/SceneServer">{{folder[0]}}-{{folder[1]}}</a><a href="carte/{{folder[0]}}/{{folder[1]}}"> [visualiser]</a></li>
		% end
	</ul>
</body>

</html>