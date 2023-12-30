CASE
	WHEN "DIFFICULTY" = 'GREEN' then color_rgb(43, 176, 28)
	WHEN "DIFFICULTY" = 'BLUE' then color_rgb(17, 93, 191)
	WHEN "DIFFICULTY" = 'BLACK' then color_rgb(0, 0, 0)
	WHEN "DIFFICULTY" = 'DOUBLE BLACK' then color_rgb(230, 25, 25)
END