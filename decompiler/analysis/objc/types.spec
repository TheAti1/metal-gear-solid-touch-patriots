STRUCT	CGSize	8	0
FIELD	0	width	f4
FIELD	4	height	f4
STRUCT	CrashLandingAppDelegate_Load	152	0
FIELD	0	filename	arr(128,i1)
FIELD	128	type	i4
FIELD	132	Num1	i4
FIELD	136	Num2	i4
FIELD	140	Num3	i4
FIELD	144	Count_max	i4
FIELD	148	Count_num	i4
STRUCT	CrashLandingAppDelegate_LoadString	20	0
FIELD	0	dimension	struct(CGSize)
FIELD	8	alignment	i4
FIELD	12	fontName	id
FIELD	16	fontSize	f4
STRUCT	CrashLandingAppDelegate_menu_data	16	0
FIELD	0	draw_num	ptr(i2)
FIELD	4	move_num	ptr(i2)
FIELD	8	back_num	i2
FIELD	10	max_num	i2
FIELD	12	select_flag	ptr(i1)
STRUCT	CGPoint	8	0
FIELD	0	x	f4
FIELD	4	y	f4
STRUCT	CrashLandingAppDelegate_Drebin_Data	32	0
FIELD	0	max_num	i2
FIELD	4	draw_num1	ptr(i2)
FIELD	8	draw_num2	ptr(i2)
FIELD	12	draw_num3	ptr(i2)
FIELD	16	icon_num	ptr(i2)
FIELD	20	money	ptr(i4)
FIELD	24	buy_flg	ptr(i1)
FIELD	28	item_num	ptr(i1)
STRUCT	CrashLandingAppDelegate_tex_Gitai	48	0
FIELD	0	img	id
FIELD	4	x	f4
FIELD	8	y	f4
FIELD	12	z	f4
FIELD	16	w	f4
FIELD	20	h	f4
FIELD	24	scale	f4
FIELD	28	drawFlg	u1
FIELD	32	eNum	i4
FIELD	36	hitflg	i4
FIELD	40	hit	struct(CGPoint)
STRUCT	CrashLandingAppDelegate_stage_obPos	24	0
FIELD	0	f0	i4
FIELD	4	f1	f4
FIELD	8	f2	f4
FIELD	12	f3	f4
FIELD	16	f4	f4
FIELD	20	f5	f4
STRUCT	CrashLandingAppDelegate_npc	12	0
FIELD	0	condition	struct(CrashLandingAppDelegate_npc_condition)
STRUCT	CrashLandingAppDelegate_npc_condition	12	0
FIELD	0	condition	ptr(struct(CrashLandingAppDelegate_npc_condition_condition))
FIELD	4	death_cnt	i4
FIELD	8	special_flag	i4
STRUCT	CrashLandingAppDelegate_npc_condition_condition	0	0
STRUCT	CrashLandingAppDelegate_item	100	0
FIELD	0	pos	struct(CrashLandingAppDelegate_stage_obPos)
FIELD	24	movePos	struct(CrashLandingAppDelegate_stage_obPos)
FIELD	48	accel	f4
FIELD	52	enemyNum	i4
FIELD	56	condition	struct(CrashLandingAppDelegate_npc_condition)
FIELD	68	gako	ptr(i4)
FIELD	72	kerotan_RPG	ptr(i4)
FIELD	76	kerotan_Stealth	ptr(i4)
FIELD	80	itemNum	i4
FIELD	84	itemNumNext	i4
FIELD	88	scale	f4
FIELD	92	death	u1
FIELD	96	distance	i4
STRUCT	EneDat	764	0
FIELD	0	param	struct(EneDat_param)
FIELD	28	pos	struct(EneDat_pos)
FIELD	52	hitX	f4
FIELD	56	hitY	f4
FIELD	60	lifeX	f4
FIELD	64	lifeY	f4
FIELD	68	lifeW	f4
FIELD	72	lifeH	f4
FIELD	76	addScale	f4
FIELD	80	addPosX	f4
FIELD	84	addPosY	f4
FIELD	88	type	i4
FIELD	92	aiAction	i4
FIELD	96	aiPattern	arr(4,i4)
FIELD	112	colNum	i4
FIELD	116	colType	ptr(i4)
FIELD	120	moveDirect	i4
FIELD	124	actNum	i4
FIELD	128	appearPoint	i4
FIELD	132	appearNum	i4
FIELD	136	aiData	ptr(struct(CrashLandingAppDelegate_npc_condition_condition))
FIELD	140	aiTimeCnt	i4
FIELD	144	aiTime	ptr(struct(CrashLandingAppDelegate_npc_condition_condition))
FIELD	148	movePos	struct(CrashLandingAppDelegate_stage_obPos)
FIELD	172	accel	f4
FIELD	176	hit	u1
FIELD	177	muteki	u1
FIELD	180	imgNum	i4
FIELD	184	stay	i4
FIELD	188	hitHp	i4
FIELD	192	cancelHp	i4
FIELD	196	distance	i4
FIELD	200	damage	i4
FIELD	204	arm_Sound	u1
FIELD	208	armer	i4
FIELD	212	anime_no	i4
FIELD	216	anime_cnt	i4
FIELD	220	anime_max_frame	i4
FIELD	224	anime_update	u1
FIELD	225	anime_reverse	u1
FIELD	226	anime_loop	u1
FIELD	228	enemyNum	i4
FIELD	232	effAtkCnt	i4
FIELD	236	eff_char	struct(EneDat_eff_char)
FIELD	392	eff_atk	struct(EneDat_eff_char)
FIELD	548	eff_hp	struct(EneDat_eff_char)
FIELD	704	waitEff	struct(EneDat_waitEff)
FIELD	744	wallHit	u1
FIELD	748	respawnTime	i4
FIELD	752	clearFactor	i4
FIELD	756	ignoreShortCut	i4
FIELD	760	takeover	i4
STRUCT	EneDat_param	28	0
FIELD	0	hp	i4
FIELD	4	max_hp	i4
FIELD	8	headShoot	i4
FIELD	12	onlyItem	i4
FIELD	16	limit	i4
FIELD	20	state	i4
FIELD	24	jumpMax	f4
STRUCT	EneDat_pos	24	0
FIELD	0	scale	f4
FIELD	4	x	f4
FIELD	8	y	f4
FIELD	12	z	f4
FIELD	16	w	i4
FIELD	20	h	i4
STRUCT	EneDat_eff_char	156	0
FIELD	0	obj_pIndex	ptr(void)
FIELD	4	obj_flag	u1
FIELD	8	obj_x	f4
FIELD	12	obj_y	f4
FIELD	16	obj_scale	f4
FIELD	20	obj_color	i4
FIELD	24	eff_type	i4
FIELD	28	eff_next	i4
FIELD	32	eff_x	f4
FIELD	36	eff_y	f4
FIELD	40	eff_scale	f4
FIELD	44	eff_rot	f4
FIELD	48	eff_color	i4
FIELD	52	eff_event	i4
FIELD	56	eff_case	i4
FIELD	60	eff_timer	u1
FIELD	64	eff_cnt	i4
FIELD	68	eff_wait	i4
FIELD	72	eff_clip	struct(CGRect)
FIELD	88	ani_state	i4
FIELD	92	ani_img	ptr(id)
FIELD	96	ani_pat	ptr(i4)
FIELD	100	ani_max	i4
FIELD	104	ani_cnt	i4
FIELD	108	ani_speed	f4
FIELD	112	ani_frame	f4
FIELD	116	dat_val	i4
FIELD	120	off_x	f4
FIELD	124	off_y	f4
FIELD	128	img_group	i4
FIELD	132	img_index	i4
FIELD	136	img_anime_no	i4
FIELD	140	img_anime_frame	i4
FIELD	144	before_eff_wait	i4
FIELD	148	before_eff_cnt	i4
FIELD	152	before_eff_type	i4
STRUCT	CGRect	16	0
FIELD	0	origin	struct(CGPoint)
FIELD	8	size	struct(CGSize)
STRUCT	EneDat_waitEff	40	0
FIELD	0	draw_flag	u1
FIELD	4	scale	f4
FIELD	8	x	f4
FIELD	12	y	f4
FIELD	16	time	i4
FIELD	20	count	i4
FIELD	24	type	i4
FIELD	28	event	i4
FIELD	32	eve_cnt	i4
FIELD	36	fade_cnt	i4
STRUCT	CrashLandingAppDelegate_drum	48	0
FIELD	0	state	i4
FIELD	4	img_num	i4
FIELD	8	scale	f4
FIELD	12	x	f4
FIELD	16	y	f4
FIELD	20	w	f4
FIELD	24	h	f4
FIELD	28	z	f4
FIELD	32	len	i4
FIELD	36	distance	i4
FIELD	40	act_wait	i4
FIELD	44	act_cnt	i4
STRUCT	CrashLandingAppDelegate_aiData	56	0
FIELD	0	act_1	i4
FIELD	4	act_2	i4
FIELD	8	act_3	i4
FIELD	12	act	arr(10,i4)
FIELD	52	nextAct	i4
STRUCT	SoundService	112	0
FIELD	0	f0	id
FIELD	4	f1	ptr(struct(SoundResourceManager))
FIELD	8	f2	i4
FIELD	12	f3	i4
FIELD	16	f4	ptr(i4)
FIELD	20	f5	ptr(i4)
FIELD	24	f6	ptr(struct(Sound))
FIELD	28	f7	ptr(ptr(struct(Sound)))
FIELD	32	f8	ptr(ptr(struct(Sound)))
FIELD	36	f9	id
FIELD	40	f10	f4
FIELD	44	f11	ptr(struct(ALCcontext_struct))
FIELD	48	f12	ptr(struct(ALCdevice_struct))
FIELD	52	f13	f4
FIELD	56	f14	f4
FIELD	60	f15	arr(3,f4)
FIELD	72	f16	bool
FIELD	73	f17	arr(3,bool)
FIELD	76	f18	f4
FIELD	80	f19	arr(3,f4)
FIELD	92	f20	f4
FIELD	96	f21	arr(3,f4)
FIELD	108	f22	bool
STRUCT	SoundResourceManager	0	0
STRUCT	Sound	0	0
STRUCT	ALCcontext_struct	0	0
STRUCT	ALCdevice_struct	0	0
STRUCT	EnemyBase_pStatus	12	0
FIELD	0	f0	i2
FIELD	2	f1	i2
FIELD	4	f2	u8
STRUCT	Canard_windBlastEffect	52	0
FIELD	0	isVisible	u1
FIELD	1	isLoop	u1
FIELD	4	pos	struct(CGPoint)
FIELD	12	pos_z	f4
FIELD	16	scale	f4
FIELD	20	scale_w	f4
FIELD	24	scale_h	f4
FIELD	28	rot	i4
FIELD	32	type	i4
FIELD	36	color	u4
FIELD	40	anime_no	i4
FIELD	44	anime_frame	i4
FIELD	48	anime_frame_max	i4
STRUCT	FBomb_data	12	0
FIELD	0	pos	struct(CGPoint)
FIELD	8	scale	f4
STRUCT	_NSRange	8	0
FIELD	0	f0	u4
FIELD	4	f1	u4
STRUCT	tagBMPDATA	68	0
FIELD	0	f0	struct(tagBITMAPFILEHEADER)
FIELD	16	f1	struct(tagBITMAPINFOHEADER)
FIELD	56	f2	ptr(i1)
FIELD	60	f3	ptr(i1)
FIELD	64	f4	ptr(i1)
STRUCT	tagBITMAPFILEHEADER	16	0
FIELD	0	f0	u2
FIELD	4	f1	u4
FIELD	8	f2	u2
FIELD	10	f3	u2
FIELD	12	f4	u4
STRUCT	tagBITMAPINFOHEADER	40	0
FIELD	0	f0	u4
FIELD	4	f1	i4
FIELD	8	f2	i4
FIELD	12	f3	u2
FIELD	14	f4	u2
FIELD	16	f5	u4
FIELD	20	f6	u4
FIELD	24	f7	i4
FIELD	28	f8	i4
FIELD	32	f9	u4
FIELD	36	f10	u4
STRUCT	__sFILE	88	0
FIELD	0	f0	ptr(i1)
FIELD	4	f1	i4
FIELD	8	f2	i4
FIELD	12	f3	i2
FIELD	14	f4	i2
FIELD	16	f5	struct(__sbuf)
FIELD	24	f6	i4
FIELD	28	f7	ptr(void)
FIELD	32	f8	ptr(void)
FIELD	36	f9	ptr(void)
FIELD	40	f10	ptr(void)
FIELD	44	f11	ptr(void)
FIELD	48	f12	struct(__sbuf)
FIELD	56	f13	ptr(struct(__sFILEX))
FIELD	60	f14	i4
FIELD	64	f15	arr(3,u1)
FIELD	67	f16	arr(1,u1)
FIELD	68	f17	struct(__sbuf)
FIELD	76	f18	i4
FIELD	80	f19	i8
STRUCT	__sbuf	8	0
FIELD	0	f0	ptr(i1)
FIELD	4	f1	i4
STRUCT	__sFILEX	0	0
STRUCT	DWUtilities_getKomaData_a0	12	0
FIELD	0	f0	i2
FIELD	2	f1	i2
FIELD	4	f2	i2
FIELD	6	f3	i2
FIELD	8	f4	i2
FIELD	10	f5	i2
STRUCT	DWUtilities_rlDataAtIndex_a0	8	0
FIELD	0	f0	i2
FIELD	2	f1	i2
FIELD	4	f2	ptr(struct(CrashLandingAppDelegate_npc_condition_condition))
STRUCT	DWUtilities_getItemData_a0	14	0
FIELD	0	f0	i2
FIELD	2	f1	i2
FIELD	4	f2	i2
FIELD	6	f3	i2
FIELD	8	f4	i2
FIELD	10	f5	i2
FIELD	12	f6	i2
STRUCT	Effect_getSpecialDamageData_a0	36	0
FIELD	0	f0	u1
FIELD	4	f1	struct(CGPoint)
FIELD	12	f2	f4
FIELD	16	f3	f4
FIELD	20	f4	i4
FIELD	24	f5	i4
FIELD	28	f6	i4
FIELD	32	f7	u4
STRUCT	Effect_getEffData_a0	216	0
FIELD	0	f0	struct(EneDat_eff_char)
FIELD	156	f1	i4
FIELD	160	f2	i4
FIELD	164	f3	i4
FIELD	168	f4	f4
FIELD	172	f5	i4
FIELD	176	f6	i4
FIELD	180	f7	struct(CGPoint)
FIELD	188	f8	i4
FIELD	192	f9	i4
FIELD	196	f10	i4
FIELD	200	f11	struct(CGRect)
STRUCT	EnemyManager_clearCheck_a3	4	0
FIELD	0	f0	i4
CLASS	Texture2D	38	
FIELD	4	_name	u4
FIELD	8	_size	struct(CGSize)
FIELD	16	_width	u4
FIELD	20	_height	u4
FIELD	24	_format	i4
FIELD	28	_maxS	f4
FIELD	32	_maxT	f4
FIELD	36	isBigTex	i1
FIELD	37	is_clamped	i1
IVARVAR	0x6c2c8	Texture2D	_name	4
IVARVAR	0x6c2cc	Texture2D	_size	8
IVARVAR	0x6c2d0	Texture2D	_width	16
IVARVAR	0x6c2d4	Texture2D	_height	20
IVARVAR	0x6c2d8	Texture2D	_format	24
IVARVAR	0x6c2dc	Texture2D	_maxS	28
IVARVAR	0x6c2e0	Texture2D	_maxT	32
IVARVAR	0x6c2e4	Texture2D	isBigTex	36
IVARVAR	0x6c2e8	Texture2D	is_clamped	37
CLASS	DWWebView	40	MimicObject
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	index	i2
FIELD	16	mimicImage	ptr(struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	20	hp	i4
FIELD	24	fade	i4
FIELD	28	fadeCount	i4
FIELD	32	fadeType	i4
FIELD	36	myWebView	id
IVARVAR	0x6c450	DWWebView	myWebView	36
CLASS	CrashLandingAppDelegate	58348	
FIELD	4	window	id
FIELD	8	_statusTexture	id
FIELD	12	_timer	id
FIELD	16	orientcnt	i4
FIELD	20	_accelValsRecieved	i1
FIELD	24	_accelDelay	i4
FIELD	28	glView	id
FIELD	32	on_ipad	i1
FIELD	33	on_iphone	i1
FIELD	36	DWGrap	id
FIELD	40	DWweb	id
FIELD	44	Start	u1
FIELD	45	SleepOn	u1
FIELD	48	_NextScene	i4
FIELD	52	_Scene	i4
FIELD	56	_BeforeScene	i4
FIELD	60	_case	i4
FIELD	64	Load	arr(256,struct(CrashLandingAppDelegate_Load))
FIELD	38976	LoadString	arr(256,struct(CrashLandingAppDelegate_LoadString))
FIELD	44096	LoadBuffer	i4
FIELD	44100	ALRL_FLG	arr(43,u1)
FIELD	44143	TX_FLG	arr(34,u1)
FIELD	44180	TX_STRING	arr(1,id)
FIELD	44184	TX_STRFLG	arr(1,u1)
FIELD	44188	Load_Texture	id
FIELD	44192	Load_count	i4
FIELD	44196	Load_Sound	arr(193,u1)
FIELD	44392	FontName	id
FIELD	44396	DiaLog	i4
FIELD	44400	DeviceInclination	u1
FIELD	44404	Data	id
FIELD	44408	pngdata	id
FIELD	44412	DATAArray	id
FIELD	44416	DataInt	i4
FIELD	44420	_timecount	i4
FIELD	44424	tex_fade	id
FIELD	44428	fade_count	f4
FIELD	44432	fade_timer	f4
FIELD	44436	fade_mode	i4
FIELD	44440	tex_menu_bar	arr(2,id)
FIELD	44448	tex_menu_bg	arr(3,id)
FIELD	44460	tex_menu_logo	arr(3,id)
FIELD	44472	tex_menu_str	arr(71,id)
FIELD	44756	tex_menu_arrow	id
FIELD	44760	tex_menu_cv	id
FIELD	44764	tex_menu_helpcv	id
FIELD	44768	tex_menu_help	arr(2,id)
FIELD	44776	tex_menu_new	id
FIELD	44780	tex_menu_txthelp	arr(11,id)
FIELD	44824	tex_menu_code	arr(15,id)
FIELD	44884	tex_menu_copyright	id
FIELD	44888	menu_data	arr(11,struct(CrashLandingAppDelegate_menu_data))
FIELD	45064	menu_scr_pos	struct(CGPoint)
FIELD	45072	Title_Lflag	u1
FIELD	45073	flg_help	u1
FIELD	45074	option_load_flag	u1
FIELD	45075	game_option_flag	u1
FIELD	45076	flg_touch	u1
FIELD	45080	title_bg_scr	arr(3,f4)
FIELD	45092	title_scr_y	arr(11,f4)
FIELD	45136	help_scr_y	f4
FIELD	45140	title_bg_alpha	arr(3,f4)
FIELD	45152	next_scene	i4
FIELD	45156	old_scene	i4
FIELD	45160	help_anim_cnt	i4
FIELD	45164	bar_anim_cnt	i4
FIELD	45168	bar_anim_num	i4
FIELD	45172	bar_anim_select	i4
FIELD	45176	back_anim_cnt	i4
FIELD	45180	help_line_num	arr(11,i4)
FIELD	45224	debug_touch	i4
FIELD	45228	FripEndCount	i4
FIELD	45232	blink_col_cnt	i4
FIELD	45236	next_col_cnt	i4
FIELD	45240	back_col_cnt	i4
FIELD	45244	menu_scroll	id
FIELD	45248	plus_scroll	id
FIELD	45252	flagBtnNext	u1
FIELD	45253	flagBtnBack	u1
FIELD	45254	MenuMoveflg	u1
FIELD	45255	immueMenuTouch	u1
FIELD	45256	tex_drebin_cv	id
FIELD	45260	tex_drebin_bar	arr(2,id)
FIELD	45268	tex_drebin_bottom	arr(2,id)
FIELD	45276	tex_drebin_icon	arr(5,id)
FIELD	45296	tex_drebin_logo	arr(2,id)
FIELD	45304	tex_drebin_menu	arr(2,id)
FIELD	45312	tex_drebin_putchase	arr(2,id)
FIELD	45320	tex_drebin_thum	arr(51,id)
FIELD	45524	tex_drebin_wall	id
FIELD	45528	tex_drebin_text_big	arr(64,id)
FIELD	45784	tex_drebin_text	arr(64,id)
FIELD	46040	tex_money	id
FIELD	46044	movie_url	id
FIELD	46048	drebin_scr_y	arr(3,f4)
FIELD	46060	drebin_scr_bottom_x	f4
FIELD	46064	drebin_select	i4
FIELD	46068	drebin_scene	i4
FIELD	46072	next_drebin_scene	i4
FIELD	46076	next_drebin_case	i4
FIELD	46080	old_drebin_case	i4
FIELD	46084	drebin_scr_x	i4
FIELD	46088	drebin_scr_x2	i4
FIELD	46092	is_drebin_announce_side	i1
FIELD	46093	is_drebin_scene	i1
FIELD	46096	Drebin_Data	arr(3,struct(CrashLandingAppDelegate_Drebin_Data))
FIELD	46192	tex_manual_bg	id
FIELD	46196	tex_manual_txt	id
FIELD	46200	tex_manual_logo	arr(2,id)
FIELD	46208	tex_manual_cv	id
FIELD	46212	tex_manual_playing	id
FIELD	46216	manual_txt_flg	u1
FIELD	46220	manual_help_line	i4
FIELD	46224	manual_select_num	i4
FIELD	46228	manual_pass_flag	u1
FIELD	46232	tex_history_bg	id
FIELD	46236	tex_history_txt	id
FIELD	46240	tex_history_cvs	id
FIELD	46244	tex_history_logo	arr(2,id)
FIELD	46252	tex_history_next	id
FIELD	46256	history_txt_flg	u1
FIELD	46260	history_scr_y	f4
FIELD	46264	history_help_line	i4
FIELD	46268	tex_logo1	id
FIELD	46272	tex_logo2	id
FIELD	46276	eneLoadNum	i4
FIELD	46280	eneLoadHai	arr(500,arr(2,i4))
FIELD	50280	tex_Gitai	arr(4,struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	50472	successionHP	i4
FIELD	50476	BGChangeFadeCount	i4
FIELD	50480	BGChangeFadeCountWait	i4
FIELD	50484	BGChangeFadeMsg	i4
FIELD	50488	BGChangeLoadStep	i4
FIELD	50492	BGChangeLoadStepWait	i4
FIELD	50496	BGChangeIsFrontFade	i1
FIELD	50497	Loading_ene	arr(100,u1)
FIELD	50600	tex_Javerin	struct(CrashLandingAppDelegate_tex_Gitai)
FIELD	50648	tex_complete	id
FIELD	50652	tex_failed	id
FIELD	50656	tex_exit	id
FIELD	50660	tex_retry	id
FIELD	50664	tex_stg_icon_pmc	id
FIELD	50668	tex_mission	id
FIELD	50672	tex_number	arr(13,id)
FIELD	50724	tex_result_str	arr(10,id)
FIELD	50764	tex_next	id
FIELD	50768	tex_advice_mk	id
FIELD	50772	tex_advice_txt	arr(2,id)
FIELD	50780	tex_advice_misson_start	id
FIELD	50784	tex_advice_logo	arr(2,id)
FIELD	50792	pIMGDATA_BGObject_tmp	ptr(struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	50796	objectNum	i4
FIELD	50800	stage_obPos	ptr(struct(CrashLandingAppDelegate_stage_obPos))
FIELD	50804	npc	struct(CrashLandingAppDelegate_npc)
FIELD	50816	item	struct(CrashLandingAppDelegate_item)
FIELD	50916	npc_char	struct(EneDat)
FIELD	51680	drum_max	i4
FIELD	51684	drum	arr(2,struct(CrashLandingAppDelegate_drum))
FIELD	51780	drum_Num	i4
FIELD	51784	drumdata	ptr(struct(CrashLandingAppDelegate_drum))
FIELD	51788	sh_case	i4
FIELD	51792	advice_case	i4
FIELD	51796	is_advice_retry	i1
FIELD	51800	result_effect	i4
FIELD	51804	result_count	i4
FIELD	51808	result_mainfont_y	f4
FIELD	51812	result_line_x	f4
FIELD	51816	result_line_y	f4
FIELD	51820	result_line_wait	i4
FIELD	51824	result_select	i4
FIELD	51828	result_fade_plus	i4
FIELD	51832	rpg_explode	struct(EneDat_eff_char)
FIELD	51988	st_pmc	i4
FIELD	51992	st_gek	i4
FIELD	51996	st_time	i4
FIELD	52000	st_time_fake	i4
FIELD	52004	hp_alpha	i4
FIELD	52008	pl_hp_w_fake	f4
FIELD	52012	en_hp_w_fake	f4
FIELD	52016	aiData	arr(19,struct(CrashLandingAppDelegate_aiData))
FIELD	53080	survival_flg	u1
FIELD	53084	tex_story_misson_start	id
FIELD	53088	tex_story_touch_any	id
FIELD	53092	tex_story_arrow	id
FIELD	53096	tex_story_cvs	id
FIELD	53100	tex_story_logo	arr(2,id)
FIELD	53108	tex_story_bg	id
FIELD	53112	tex_story_txt	id
FIELD	53116	flg_storytxt	u1
FIELD	53120	story_line_num	i4
FIELD	53124	story_scr_y	f4
FIELD	53128	aiNum	arr(10,i4)
FIELD	53168	tex_clear_condition_logo	arr(2,id)
FIELD	53176	tex_clear_condition_icon	id
FIELD	53180	tex_clear_condition_txt	arr(6,id)
FIELD	53204	tex_credit_txt	arr(3,id)
FIELD	53216	credit_scr_y	f4
FIELD	53220	credit_line_num	i4
FIELD	53224	textBuffer	arr(5120,i1)
FIELD	58344	tex_loading_msg	id
IVARVAR	0x6dd10	CrashLandingAppDelegate	window	4
IVARVAR	0x6dd14	CrashLandingAppDelegate	_statusTexture	8
IVARVAR	0x6dd18	CrashLandingAppDelegate	_timer	12
IVARVAR	0x6dd1c	CrashLandingAppDelegate	orientcnt	16
IVARVAR	0x6dd20	CrashLandingAppDelegate	_accelValsRecieved	20
IVARVAR	0x6dd24	CrashLandingAppDelegate	_accelDelay	24
IVARVAR	0x6dd28	CrashLandingAppDelegate	glView	28
IVARVAR	0x6dd2c	CrashLandingAppDelegate	on_ipad	32
IVARVAR	0x6dd30	CrashLandingAppDelegate	on_iphone	33
IVARVAR	0x6dd34	CrashLandingAppDelegate	DWGrap	36
IVARVAR	0x6dd38	CrashLandingAppDelegate	DWweb	40
IVARVAR	0x6dd3c	CrashLandingAppDelegate	Start	44
IVARVAR	0x6dd40	CrashLandingAppDelegate	SleepOn	45
IVARVAR	0x6dd44	CrashLandingAppDelegate	_NextScene	48
IVARVAR	0x6dd48	CrashLandingAppDelegate	_Scene	52
IVARVAR	0x6dd4c	CrashLandingAppDelegate	_BeforeScene	56
IVARVAR	0x6dd50	CrashLandingAppDelegate	_case	60
IVARVAR	0x6dd54	CrashLandingAppDelegate	Load	64
IVARVAR	0x6dd58	CrashLandingAppDelegate	LoadString	38976
IVARVAR	0x6dd5c	CrashLandingAppDelegate	LoadBuffer	44096
IVARVAR	0x6dd60	CrashLandingAppDelegate	ALRL_FLG	44100
IVARVAR	0x6dd64	CrashLandingAppDelegate	TX_FLG	44143
IVARVAR	0x6dd68	CrashLandingAppDelegate	TX_STRING	44180
IVARVAR	0x6dd6c	CrashLandingAppDelegate	TX_STRFLG	44184
IVARVAR	0x6dd70	CrashLandingAppDelegate	Load_Texture	44188
IVARVAR	0x6dd74	CrashLandingAppDelegate	Load_count	44192
IVARVAR	0x6dd78	CrashLandingAppDelegate	Load_Sound	44196
IVARVAR	0x6dd7c	CrashLandingAppDelegate	FontName	44392
IVARVAR	0x6dd80	CrashLandingAppDelegate	DiaLog	44396
IVARVAR	0x6dd84	CrashLandingAppDelegate	DeviceInclination	44400
IVARVAR	0x6dd88	CrashLandingAppDelegate	Data	44404
IVARVAR	0x6dd8c	CrashLandingAppDelegate	pngdata	44408
IVARVAR	0x6dd90	CrashLandingAppDelegate	DATAArray	44412
IVARVAR	0x6dd94	CrashLandingAppDelegate	DataInt	44416
IVARVAR	0x6dd98	CrashLandingAppDelegate	_timecount	44420
IVARVAR	0x6dd9c	CrashLandingAppDelegate	tex_fade	44424
IVARVAR	0x6dda0	CrashLandingAppDelegate	fade_count	44428
IVARVAR	0x6dda4	CrashLandingAppDelegate	fade_timer	44432
IVARVAR	0x6dda8	CrashLandingAppDelegate	fade_mode	44436
IVARVAR	0x6ddac	CrashLandingAppDelegate	tex_menu_bar	44440
IVARVAR	0x6ddb0	CrashLandingAppDelegate	tex_menu_bg	44448
IVARVAR	0x6ddb4	CrashLandingAppDelegate	tex_menu_logo	44460
IVARVAR	0x6ddb8	CrashLandingAppDelegate	tex_menu_str	44472
IVARVAR	0x6ddbc	CrashLandingAppDelegate	tex_menu_arrow	44756
IVARVAR	0x6ddc0	CrashLandingAppDelegate	tex_menu_cv	44760
IVARVAR	0x6ddc4	CrashLandingAppDelegate	tex_menu_helpcv	44764
IVARVAR	0x6ddc8	CrashLandingAppDelegate	tex_menu_help	44768
IVARVAR	0x6ddcc	CrashLandingAppDelegate	tex_menu_new	44776
IVARVAR	0x6ddd0	CrashLandingAppDelegate	tex_menu_txthelp	44780
IVARVAR	0x6ddd4	CrashLandingAppDelegate	tex_menu_code	44824
IVARVAR	0x6ddd8	CrashLandingAppDelegate	tex_menu_copyright	44884
IVARVAR	0x6dddc	CrashLandingAppDelegate	menu_data	44888
IVARVAR	0x6dde0	CrashLandingAppDelegate	menu_scr_pos	45064
IVARVAR	0x6dde4	CrashLandingAppDelegate	Title_Lflag	45072
IVARVAR	0x6dde8	CrashLandingAppDelegate	flg_help	45073
IVARVAR	0x6ddec	CrashLandingAppDelegate	option_load_flag	45074
IVARVAR	0x6ddf0	CrashLandingAppDelegate	game_option_flag	45075
IVARVAR	0x6ddf4	CrashLandingAppDelegate	flg_touch	45076
IVARVAR	0x6ddf8	CrashLandingAppDelegate	title_bg_scr	45080
IVARVAR	0x6ddfc	CrashLandingAppDelegate	title_scr_y	45092
IVARVAR	0x6de00	CrashLandingAppDelegate	help_scr_y	45136
IVARVAR	0x6de04	CrashLandingAppDelegate	title_bg_alpha	45140
IVARVAR	0x6de08	CrashLandingAppDelegate	next_scene	45152
IVARVAR	0x6de0c	CrashLandingAppDelegate	old_scene	45156
IVARVAR	0x6de10	CrashLandingAppDelegate	help_anim_cnt	45160
IVARVAR	0x6de14	CrashLandingAppDelegate	bar_anim_cnt	45164
IVARVAR	0x6de18	CrashLandingAppDelegate	bar_anim_num	45168
IVARVAR	0x6de1c	CrashLandingAppDelegate	bar_anim_select	45172
IVARVAR	0x6de20	CrashLandingAppDelegate	back_anim_cnt	45176
IVARVAR	0x6de24	CrashLandingAppDelegate	help_line_num	45180
IVARVAR	0x6de28	CrashLandingAppDelegate	debug_touch	45224
IVARVAR	0x6de2c	CrashLandingAppDelegate	FripEndCount	45228
IVARVAR	0x6de30	CrashLandingAppDelegate	blink_col_cnt	45232
IVARVAR	0x6de34	CrashLandingAppDelegate	next_col_cnt	45236
IVARVAR	0x6de38	CrashLandingAppDelegate	back_col_cnt	45240
IVARVAR	0x6de3c	CrashLandingAppDelegate	menu_scroll	45244
IVARVAR	0x6de40	CrashLandingAppDelegate	plus_scroll	45248
IVARVAR	0x6de44	CrashLandingAppDelegate	flagBtnNext	45252
IVARVAR	0x6de48	CrashLandingAppDelegate	flagBtnBack	45253
IVARVAR	0x6de4c	CrashLandingAppDelegate	MenuMoveflg	45254
IVARVAR	0x6de50	CrashLandingAppDelegate	immueMenuTouch	45255
IVARVAR	0x6de54	CrashLandingAppDelegate	tex_drebin_cv	45256
IVARVAR	0x6de58	CrashLandingAppDelegate	tex_drebin_bar	45260
IVARVAR	0x6de5c	CrashLandingAppDelegate	tex_drebin_bottom	45268
IVARVAR	0x6de60	CrashLandingAppDelegate	tex_drebin_icon	45276
IVARVAR	0x6de64	CrashLandingAppDelegate	tex_drebin_logo	45296
IVARVAR	0x6de68	CrashLandingAppDelegate	tex_drebin_menu	45304
IVARVAR	0x6de6c	CrashLandingAppDelegate	tex_drebin_putchase	45312
IVARVAR	0x6de70	CrashLandingAppDelegate	tex_drebin_thum	45320
IVARVAR	0x6de74	CrashLandingAppDelegate	tex_drebin_wall	45524
IVARVAR	0x6de78	CrashLandingAppDelegate	tex_drebin_text_big	45528
IVARVAR	0x6de7c	CrashLandingAppDelegate	tex_drebin_text	45784
IVARVAR	0x6de80	CrashLandingAppDelegate	tex_money	46040
IVARVAR	0x6de84	CrashLandingAppDelegate	movie_url	46044
IVARVAR	0x6de88	CrashLandingAppDelegate	drebin_scr_y	46048
IVARVAR	0x6de8c	CrashLandingAppDelegate	drebin_scr_bottom_x	46060
IVARVAR	0x6de90	CrashLandingAppDelegate	drebin_select	46064
IVARVAR	0x6de94	CrashLandingAppDelegate	drebin_scene	46068
IVARVAR	0x6de98	CrashLandingAppDelegate	next_drebin_scene	46072
IVARVAR	0x6de9c	CrashLandingAppDelegate	next_drebin_case	46076
IVARVAR	0x6dea0	CrashLandingAppDelegate	old_drebin_case	46080
IVARVAR	0x6dea4	CrashLandingAppDelegate	drebin_scr_x	46084
IVARVAR	0x6dea8	CrashLandingAppDelegate	drebin_scr_x2	46088
IVARVAR	0x6deac	CrashLandingAppDelegate	is_drebin_announce_side	46092
IVARVAR	0x6deb0	CrashLandingAppDelegate	is_drebin_scene	46093
IVARVAR	0x6deb4	CrashLandingAppDelegate	Drebin_Data	46096
IVARVAR	0x6deb8	CrashLandingAppDelegate	tex_manual_bg	46192
IVARVAR	0x6debc	CrashLandingAppDelegate	tex_manual_txt	46196
IVARVAR	0x6dec0	CrashLandingAppDelegate	tex_manual_logo	46200
IVARVAR	0x6dec4	CrashLandingAppDelegate	tex_manual_cv	46208
IVARVAR	0x6dec8	CrashLandingAppDelegate	tex_manual_playing	46212
IVARVAR	0x6decc	CrashLandingAppDelegate	manual_txt_flg	46216
IVARVAR	0x6ded0	CrashLandingAppDelegate	manual_help_line	46220
IVARVAR	0x6ded4	CrashLandingAppDelegate	manual_select_num	46224
IVARVAR	0x6ded8	CrashLandingAppDelegate	manual_pass_flag	46228
IVARVAR	0x6dedc	CrashLandingAppDelegate	tex_history_bg	46232
IVARVAR	0x6dee0	CrashLandingAppDelegate	tex_history_txt	46236
IVARVAR	0x6dee4	CrashLandingAppDelegate	tex_history_cvs	46240
IVARVAR	0x6dee8	CrashLandingAppDelegate	tex_history_logo	46244
IVARVAR	0x6deec	CrashLandingAppDelegate	tex_history_next	46252
IVARVAR	0x6def0	CrashLandingAppDelegate	history_txt_flg	46256
IVARVAR	0x6def4	CrashLandingAppDelegate	history_scr_y	46260
IVARVAR	0x6def8	CrashLandingAppDelegate	history_help_line	46264
IVARVAR	0x6defc	CrashLandingAppDelegate	tex_logo1	46268
IVARVAR	0x6df00	CrashLandingAppDelegate	tex_logo2	46272
IVARVAR	0x6df04	CrashLandingAppDelegate	eneLoadNum	46276
IVARVAR	0x6df08	CrashLandingAppDelegate	eneLoadHai	46280
IVARVAR	0x6df0c	CrashLandingAppDelegate	tex_Gitai	50280
IVARVAR	0x6df10	CrashLandingAppDelegate	successionHP	50472
IVARVAR	0x6df14	CrashLandingAppDelegate	BGChangeFadeCount	50476
IVARVAR	0x6df18	CrashLandingAppDelegate	BGChangeFadeCountWait	50480
IVARVAR	0x6df1c	CrashLandingAppDelegate	BGChangeFadeMsg	50484
IVARVAR	0x6df20	CrashLandingAppDelegate	BGChangeLoadStep	50488
IVARVAR	0x6df24	CrashLandingAppDelegate	BGChangeLoadStepWait	50492
IVARVAR	0x6df28	CrashLandingAppDelegate	BGChangeIsFrontFade	50496
IVARVAR	0x6df2c	CrashLandingAppDelegate	Loading_ene	50497
IVARVAR	0x6df30	CrashLandingAppDelegate	tex_Javerin	50600
IVARVAR	0x6df34	CrashLandingAppDelegate	tex_complete	50648
IVARVAR	0x6df38	CrashLandingAppDelegate	tex_failed	50652
IVARVAR	0x6df3c	CrashLandingAppDelegate	tex_exit	50656
IVARVAR	0x6df40	CrashLandingAppDelegate	tex_retry	50660
IVARVAR	0x6df44	CrashLandingAppDelegate	tex_stg_icon_pmc	50664
IVARVAR	0x6df48	CrashLandingAppDelegate	tex_mission	50668
IVARVAR	0x6df4c	CrashLandingAppDelegate	tex_number	50672
IVARVAR	0x6df50	CrashLandingAppDelegate	tex_result_str	50724
IVARVAR	0x6df54	CrashLandingAppDelegate	tex_next	50764
IVARVAR	0x6df58	CrashLandingAppDelegate	tex_advice_mk	50768
IVARVAR	0x6df5c	CrashLandingAppDelegate	tex_advice_txt	50772
IVARVAR	0x6df60	CrashLandingAppDelegate	tex_advice_misson_start	50780
IVARVAR	0x6df64	CrashLandingAppDelegate	tex_advice_logo	50784
IVARVAR	0x6df68	CrashLandingAppDelegate	pIMGDATA_BGObject_tmp	50792
IVARVAR	0x6df6c	CrashLandingAppDelegate	objectNum	50796
IVARVAR	0x6df70	CrashLandingAppDelegate	stage_obPos	50800
IVARVAR	0x6df74	CrashLandingAppDelegate	npc	50804
IVARVAR	0x6df78	CrashLandingAppDelegate	item	50816
IVARVAR	0x6df7c	CrashLandingAppDelegate	npc_char	50916
IVARVAR	0x6df80	CrashLandingAppDelegate	drum_max	51680
IVARVAR	0x6df84	CrashLandingAppDelegate	drum	51684
IVARVAR	0x6df88	CrashLandingAppDelegate	drum_Num	51780
IVARVAR	0x6df8c	CrashLandingAppDelegate	drumdata	51784
IVARVAR	0x6df90	CrashLandingAppDelegate	sh_case	51788
IVARVAR	0x6df94	CrashLandingAppDelegate	advice_case	51792
IVARVAR	0x6df98	CrashLandingAppDelegate	is_advice_retry	51796
IVARVAR	0x6df9c	CrashLandingAppDelegate	result_effect	51800
IVARVAR	0x6dfa0	CrashLandingAppDelegate	result_count	51804
IVARVAR	0x6dfa4	CrashLandingAppDelegate	result_mainfont_y	51808
IVARVAR	0x6dfa8	CrashLandingAppDelegate	result_line_x	51812
IVARVAR	0x6dfac	CrashLandingAppDelegate	result_line_y	51816
IVARVAR	0x6dfb0	CrashLandingAppDelegate	result_line_wait	51820
IVARVAR	0x6dfb4	CrashLandingAppDelegate	result_select	51824
IVARVAR	0x6dfb8	CrashLandingAppDelegate	result_fade_plus	51828
IVARVAR	0x6dfbc	CrashLandingAppDelegate	rpg_explode	51832
IVARVAR	0x6dfc0	CrashLandingAppDelegate	st_pmc	51988
IVARVAR	0x6dfc4	CrashLandingAppDelegate	st_gek	51992
IVARVAR	0x6dfc8	CrashLandingAppDelegate	st_time	51996
IVARVAR	0x6dfcc	CrashLandingAppDelegate	st_time_fake	52000
IVARVAR	0x6dfd0	CrashLandingAppDelegate	hp_alpha	52004
IVARVAR	0x6dfd4	CrashLandingAppDelegate	pl_hp_w_fake	52008
IVARVAR	0x6dfd8	CrashLandingAppDelegate	en_hp_w_fake	52012
IVARVAR	0x6dfdc	CrashLandingAppDelegate	aiData	52016
IVARVAR	0x6dfe0	CrashLandingAppDelegate	survival_flg	53080
IVARVAR	0x6dfe4	CrashLandingAppDelegate	tex_story_misson_start	53084
IVARVAR	0x6dfe8	CrashLandingAppDelegate	tex_story_touch_any	53088
IVARVAR	0x6dfec	CrashLandingAppDelegate	tex_story_arrow	53092
IVARVAR	0x6dff0	CrashLandingAppDelegate	tex_story_cvs	53096
IVARVAR	0x6dff4	CrashLandingAppDelegate	tex_story_logo	53100
IVARVAR	0x6dff8	CrashLandingAppDelegate	tex_story_bg	53108
IVARVAR	0x6dffc	CrashLandingAppDelegate	tex_story_txt	53112
IVARVAR	0x6e000	CrashLandingAppDelegate	flg_storytxt	53116
IVARVAR	0x6e004	CrashLandingAppDelegate	story_line_num	53120
IVARVAR	0x6e008	CrashLandingAppDelegate	story_scr_y	53124
IVARVAR	0x6e00c	CrashLandingAppDelegate	aiNum	53128
IVARVAR	0x6e010	CrashLandingAppDelegate	tex_clear_condition_logo	53168
IVARVAR	0x6e014	CrashLandingAppDelegate	tex_clear_condition_icon	53176
IVARVAR	0x6e018	CrashLandingAppDelegate	tex_clear_condition_txt	53180
IVARVAR	0x6e01c	CrashLandingAppDelegate	tex_credit_txt	53204
IVARVAR	0x6e020	CrashLandingAppDelegate	credit_scr_y	53216
IVARVAR	0x6e024	CrashLandingAppDelegate	credit_line_num	53220
IVARVAR	0x6e028	CrashLandingAppDelegate	textBuffer	53224
IVARVAR	0x6e02c	CrashLandingAppDelegate	tex_loading_msg	58344
CLASS	SoundThread	16	
FIELD	4	mSoundService	ptr(struct(SoundService))
FIELD	8	mThreadLoop	bool
FIELD	12	mLock	id
IVARVAR	0x6e28c	SoundThread	mSoundService	4
IVARVAR	0x6e290	SoundThread	mThreadLoop	8
IVARVAR	0x6e294	SoundThread	mLock	12
CLASS	DWGraphics	68	
FIELD	4	col_a	f4
FIELD	8	col_r	f4
FIELD	12	col_g	f4
FIELD	16	col_b	f4
FIELD	20	fontName	id
FIELD	24	fontSize	i4
FIELD	28	StringTexture	arr(2,id)
FIELD	36	RectTexture	arr(7,id)
FIELD	64	LoadBer	f4
IVARVAR	0x6e5a4	DWGraphics	col_a	4
IVARVAR	0x6e5a8	DWGraphics	col_r	8
IVARVAR	0x6e5ac	DWGraphics	col_g	12
IVARVAR	0x6e5b0	DWGraphics	col_b	16
IVARVAR	0x6e5b4	DWGraphics	fontName	20
IVARVAR	0x6e5b8	DWGraphics	fontSize	24
IVARVAR	0x6e5bc	DWGraphics	StringTexture	28
IVARVAR	0x6e5c0	DWGraphics	RectTexture	36
IVARVAR	0x6e5c4	DWGraphics	LoadBer	64
CLASS	PMC	56	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	missile	id
IVARVAR	0x6ecb4	PMC	missile	52
CLASS	EnemyBase	52	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
IVARVAR	0x6f5c0	EnemyBase	pEneDat	12
IVARVAR	0x6f5c4	EnemyBase	pStatus	16
IVARVAR	0x6f5c8	EnemyBase	timer	20
IVARVAR	0x6f5cc	EnemyBase	index	24
IVARVAR	0x6f5d0	EnemyBase	appear	26
IVARVAR	0x6f5d4	EnemyBase	sign	28
IVARVAR	0x6f5d8	EnemyBase	attack	30
IVARVAR	0x6f5dc	EnemyBase	move	32
IVARVAR	0x6f5e0	EnemyBase	aiControl	34
IVARVAR	0x6f5e4	EnemyBase	aiStep	36
IVARVAR	0x6f5e8	EnemyBase	attackTime	38
IVARVAR	0x6f5ec	EnemyBase	fade	40
IVARVAR	0x6f5f0	EnemyBase	limit	42
IVARVAR	0x6f5f4	EnemyBase	didHitMissile	44
IVARVAR	0x6f5f8	EnemyBase	didDisappeard	45
IVARVAR	0x6f5fc	EnemyBase	wallHitType	48
CLASS	Canard	148	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	ConardMoveRot	f4
FIELD	56	MoveSpeed	f4
FIELD	60	velocityX	f4
FIELD	64	velocityY	f4
FIELD	68	velocityZ	f4
FIELD	72	height	f4
FIELD	76	bottom	f4
FIELD	80	time	i4
FIELD	84	ConardMovetype	i2
FIELD	86	MoveCount	i2
FIELD	88	attackCount	i2
FIELD	92	missile	id
FIELD	96	windBlastEffect	struct(Canard_windBlastEffect)
IVARVAR	0x6f86c	Canard	ConardMoveRot	52
IVARVAR	0x6f870	Canard	MoveSpeed	56
IVARVAR	0x6f874	Canard	velocityX	60
IVARVAR	0x6f878	Canard	velocityY	64
IVARVAR	0x6f87c	Canard	velocityZ	68
IVARVAR	0x6f880	Canard	height	72
IVARVAR	0x6f884	Canard	bottom	76
IVARVAR	0x6f888	Canard	time	80
IVARVAR	0x6f88c	Canard	ConardMovetype	84
IVARVAR	0x6f890	Canard	MoveCount	86
IVARVAR	0x6f894	Canard	attackCount	88
IVARVAR	0x6f898	Canard	missile	92
IVARVAR	0x6f89c	Canard	windBlastEffect	96
CLASS	PoweredSuit	104	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	landEffect	struct(Canard_windBlastEffect)
IVARVAR	0x6f9e8	PoweredSuit	landEffect	52
CLASS	Gekko	184	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	recoverTimer	i2
FIELD	54	moveRateFar	i2
FIELD	56	moveRateMiddle	i2
FIELD	58	moveRateNear	i2
FIELD	60	moveRateTimer	i2
FIELD	62	moveDestination	i2
FIELD	64	cancelHpThreshold	i4
FIELD	68	originalAppearPoint	i2
FIELD	72	movablePoints	u8
FIELD	80	jumpEffect	struct(Canard_windBlastEffect)
FIELD	132	landEffect	struct(Canard_windBlastEffect)
IVARVAR	0x6fce0	Gekko	recoverTimer	52
IVARVAR	0x6fce4	Gekko	moveRateFar	54
IVARVAR	0x6fce8	Gekko	moveRateMiddle	56
IVARVAR	0x6fcec	Gekko	moveRateNear	58
IVARVAR	0x6fcf0	Gekko	moveRateTimer	60
IVARVAR	0x6fcf4	Gekko	moveDestination	62
IVARVAR	0x6fcf8	Gekko	cancelHpThreshold	64
IVARVAR	0x6fcfc	Gekko	originalAppearPoint	68
IVARVAR	0x6fd00	Gekko	movablePoints	72
IVARVAR	0x6fd04	Gekko	jumpEffect	80
IVARVAR	0x6fd08	Gekko	landEffect	132
CLASS	Octopus	120	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	moveFlag	u1
FIELD	53	isStick	u1
FIELD	56	blueFireWaitTimer	i4
FIELD	60	successionHP	ptr(i4)
FIELD	64	mimic	arr(4,id)
FIELD	80	SEinterval	i4
FIELD	84	mimicID	i4
FIELD	88	FBombCount	i4
FIELD	92	FBombInterval	i4
FIELD	96	FBombs	arr(6,id)
IVARVAR	0x6ff80	Octopus	moveFlag	52
IVARVAR	0x6ff84	Octopus	isStick	53
IVARVAR	0x6ff88	Octopus	blueFireWaitTimer	56
IVARVAR	0x6ff8c	Octopus	successionHP	60
IVARVAR	0x6ff90	Octopus	mimic	64
IVARVAR	0x6ff94	Octopus	SEinterval	80
IVARVAR	0x6ff98	Octopus	mimicID	84
IVARVAR	0x6ff9c	Octopus	FBombCount	88
IVARVAR	0x6ffa0	Octopus	FBombInterval	92
IVARVAR	0x6ffa4	Octopus	FBombs	96
CLASS	MyEAGLView	176	
FIELD	33	on_ipad	i1
FIELD	36	backingWidth	i4
FIELD	40	backingHeight	i4
FIELD	44	context	id
FIELD	48	viewRenderbuffer	u4
FIELD	52	viewFramebuffer	u4
FIELD	56	depthRenderbuffer	u4
FIELD	60	tEvent_state	arr(2,u4)
FIELD	68	startTouchPos	arr(2,struct(CGPoint))
FIELD	84	moveTouchPos	arr(2,struct(CGPoint))
FIELD	100	moveTouchPos_Old	arr(2,struct(CGPoint))
FIELD	116	endTouchPos	arr(2,struct(CGPoint))
FIELD	132	touch_in	arr(2,u1)
FIELD	134	touch_out	arr(2,u1)
FIELD	136	touch_move	arr(2,u1)
FIELD	138	touchFlag	arr(2,u1)
FIELD	140	touch_time	arr(2,i4)
FIELD	148	touch_move_time	arr(2,i4)
FIELD	156	MultiTouchflg	u1
FIELD	160	StandardDistance	f4
FIELD	164	Distance	f4
FIELD	168	StandardRatio	f4
FIELD	172	Ratio	f4
IVARVAR	0x70358	MyEAGLView	on_ipad	33
IVARVAR	0x7035c	MyEAGLView	backingWidth	36
IVARVAR	0x70360	MyEAGLView	backingHeight	40
IVARVAR	0x6ffa8	MyEAGLView	context	44
IVARVAR	0x70364	MyEAGLView	viewRenderbuffer	48
IVARVAR	0x70368	MyEAGLView	viewFramebuffer	52
IVARVAR	0x7036c	MyEAGLView	depthRenderbuffer	56
IVARVAR	0x70370	MyEAGLView	tEvent_state	60
IVARVAR	0x70374	MyEAGLView	startTouchPos	68
IVARVAR	0x70378	MyEAGLView	moveTouchPos	84
IVARVAR	0x7037c	MyEAGLView	moveTouchPos_Old	100
IVARVAR	0x70380	MyEAGLView	endTouchPos	116
IVARVAR	0x70384	MyEAGLView	touch_in	132
IVARVAR	0x70388	MyEAGLView	touch_out	134
IVARVAR	0x7038c	MyEAGLView	touch_move	136
IVARVAR	0x70390	MyEAGLView	touchFlag	138
IVARVAR	0x70394	MyEAGLView	touch_time	140
IVARVAR	0x70398	MyEAGLView	touch_move_time	148
IVARVAR	0x7039c	MyEAGLView	MultiTouchflg	156
IVARVAR	0x703a0	MyEAGLView	StandardDistance	160
IVARVAR	0x703a4	MyEAGLView	Distance	164
IVARVAR	0x703a8	MyEAGLView	StandardRatio	168
IVARVAR	0x703ac	MyEAGLView	Ratio	172
CLASS	Missile	692	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	MissileImage	struct(CrashLandingAppDelegate_tex_Gitai)
FIELD	72	SmokeImages	arr(12,struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	648	pRpgExplosion	ptr(struct(EneDat_eff_char))
FIELD	652	posz	f4
FIELD	656	missileType	i4
FIELD	660	missileAccel	f4
FIELD	664	missileAccelBase	f4
FIELD	668	img_group	i4
FIELD	672	img_index	i4
FIELD	676	img_anime	i4
FIELD	680	img_frame	i4
FIELD	684	img_frame_max	i4
FIELD	688	side	i4
IVARVAR	0x70550	Missile	MissileImage	24
IVARVAR	0x70554	Missile	SmokeImages	72
IVARVAR	0x70558	Missile	pRpgExplosion	648
IVARVAR	0x7055c	Missile	posz	652
IVARVAR	0x70560	Missile	missileType	656
IVARVAR	0x70564	Missile	missileAccel	660
IVARVAR	0x70568	Missile	missileAccelBase	664
IVARVAR	0x7056c	Missile	img_group	668
IVARVAR	0x70570	Missile	img_index	672
IVARVAR	0x70574	Missile	img_anime	676
IVARVAR	0x70578	Missile	img_frame	680
IVARVAR	0x7057c	Missile	img_frame_max	684
IVARVAR	0x70580	Missile	side	688
CLASS	WeaponBase	24	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
IVARVAR	0x7066c	WeaponBase	type	12
IVARVAR	0x70670	WeaponBase	pEneDat	16
IVARVAR	0x70674	WeaponBase	damage	20
CLASS	MenuScroll	88	
FIELD	4	touchFlag	i1
FIELD	8	touchPoint	struct(CGPoint)
FIELD	16	movePoint	struct(CGPoint)
FIELD	24	movePointOld	struct(CGPoint)
FIELD	32	scrollSize	struct(CGSize)
FIELD	40	scrollOverRange	f4
FIELD	44	isScroll	i1
FIELD	45	isMove	i1
FIELD	46	isFlick	i1
FIELD	48	flickArrow	f4
FIELD	52	flickTimer	f4
FIELD	56	flickSpeed	f4
FIELD	60	scrollPos	f4
FIELD	64	scrollPosPrv	f4
FIELD	68	scrollPosOld	f4
FIELD	72	scrollPosOver	f4
FIELD	76	scrollPosOverDef	f4
FIELD	80	scrollReflectCnt	f4
FIELD	84	scrollReflectValue	f4
IVARVAR	0x711cc	MenuScroll	touchFlag	4
IVARVAR	0x711d0	MenuScroll	touchPoint	8
IVARVAR	0x711d4	MenuScroll	movePoint	16
IVARVAR	0x711d8	MenuScroll	movePointOld	24
IVARVAR	0x711dc	MenuScroll	scrollSize	32
IVARVAR	0x711e0	MenuScroll	scrollOverRange	40
IVARVAR	0x711e4	MenuScroll	isScroll	44
IVARVAR	0x711e8	MenuScroll	isMove	45
IVARVAR	0x711ec	MenuScroll	isFlick	46
IVARVAR	0x711f0	MenuScroll	flickArrow	48
IVARVAR	0x711f4	MenuScroll	flickTimer	52
IVARVAR	0x711f8	MenuScroll	flickSpeed	56
IVARVAR	0x711fc	MenuScroll	scrollPos	60
IVARVAR	0x71200	MenuScroll	scrollPosPrv	64
IVARVAR	0x71204	MenuScroll	scrollPosOld	68
IVARVAR	0x71208	MenuScroll	scrollPosOver	72
IVARVAR	0x7120c	MenuScroll	scrollPosOverDef	76
IVARVAR	0x71210	MenuScroll	scrollReflectCnt	80
IVARVAR	0x71214	MenuScroll	scrollReflectValue	84
CLASS	ObjectBase	12	
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
IVARVAR	0x71324	ObjectBase	_type	4
IVARVAR	0x71328	ObjectBase	z	8
CLASS	Item	173	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	item	ptr(struct(CrashLandingAppDelegate_item))
FIELD	16	eff_item	struct(EneDat_eff_char)
FIELD	172	direct	u1
IVARVAR	0x71458	Item	item	12
IVARVAR	0x7145c	Item	eff_item	16
IVARVAR	0x71460	Item	direct	172
CLASS	Drum	18	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	drum	ptr(struct(CrashLandingAppDelegate_drum))
FIELD	16	index	i2
IVARVAR	0x71540	Drum	drum	12
IVARVAR	0x71544	Drum	index	16
CLASS	BGObject	32	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	index	i2
FIELD	16	pIMAGE_DATA	ptr(struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	20	obj_distance	i4
FIELD	24	drawScaleW	f4
FIELD	28	drawScaleH	f4
IVARVAR	0x71648	BGObject	index	12
IVARVAR	0x7164c	BGObject	pIMAGE_DATA	16
IVARVAR	0x71650	BGObject	obj_distance	20
IVARVAR	0x71654	BGObject	drawScaleW	24
IVARVAR	0x71658	BGObject	drawScaleH	28
CLASS	MimicObject	36	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	index	i2
FIELD	16	mimicImage	ptr(struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	20	hp	i4
FIELD	24	fade	i4
FIELD	28	fadeCount	i4
FIELD	32	fadeType	i4
IVARVAR	0x7177c	MimicObject	index	12
IVARVAR	0x71780	MimicObject	mimicImage	16
IVARVAR	0x71784	MimicObject	hp	20
IVARVAR	0x71788	MimicObject	fade	24
IVARVAR	0x7178c	MimicObject	fadeCount	28
IVARVAR	0x71790	MimicObject	fadeType	32
CLASS	Raven	208	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	appearRaven	i1
FIELD	53	checkSlider	arr(6,i1)
FIELD	60	maxSlider	i4
FIELD	64	nowSlider	i4
FIELD	68	stageno	i4
FIELD	72	linearrow	i1
FIELD	76	linechk1	i4
FIELD	80	linechk2	i4
FIELD	84	lineno	i4
FIELD	88	timeWait	i4
FIELD	92	timeBomb	i4
FIELD	96	timeFlap	i4
FIELD	100	scaleAccel	f4
FIELD	104	isSpecial	i1
FIELD	105	isEscapeSE	i1
FIELD	108	alphaEscaple	i4
FIELD	112	pGrenade	id
FIELD	116	pBomb	id
FIELD	120	pSlider	arr(6,id)
FIELD	144	windBlastEffect	struct(Canard_windBlastEffect)
FIELD	196	typeHit	i4
FIELD	200	successionHP	ptr(i4)
FIELD	204	posz	f4
IVARVAR	0x71b10	Raven	appearRaven	52
IVARVAR	0x71b14	Raven	checkSlider	53
IVARVAR	0x71b18	Raven	maxSlider	60
IVARVAR	0x71b1c	Raven	nowSlider	64
IVARVAR	0x71b20	Raven	stageno	68
IVARVAR	0x71b24	Raven	linearrow	72
IVARVAR	0x71b28	Raven	linechk1	76
IVARVAR	0x71b2c	Raven	linechk2	80
IVARVAR	0x71b30	Raven	lineno	84
IVARVAR	0x71b34	Raven	timeWait	88
IVARVAR	0x71b38	Raven	timeBomb	92
IVARVAR	0x71b3c	Raven	timeFlap	96
IVARVAR	0x71b40	Raven	scaleAccel	100
IVARVAR	0x71b44	Raven	isSpecial	104
IVARVAR	0x71b48	Raven	isEscapeSE	105
IVARVAR	0x71b4c	Raven	alphaEscaple	108
IVARVAR	0x71b50	Raven	pGrenade	112
IVARVAR	0x71b54	Raven	pBomb	116
IVARVAR	0x71b58	Raven	pSlider	120
IVARVAR	0x71b5c	Raven	windBlastEffect	144
IVARVAR	0x71b60	Raven	typeHit	196
IVARVAR	0x71b64	Raven	successionHP	200
IVARVAR	0x71b68	Raven	posz	204
CLASS	EffectObject	18	ObjectBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	effectType	i4
FIELD	16	index	i2
IVARVAR	0x71c18	EffectObject	effectType	12
IVARVAR	0x71c1c	EffectObject	index	16
CLASS	RavenSlider	880	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	sliderNo	i4
FIELD	28	WeaponData	struct(EneDat)
FIELD	792	isDisp	i1
FIELD	793	isDammage	i1
FIELD	794	isEscape	i1
FIELD	795	isBroken	i1
FIELD	796	isHead	i1
FIELD	797	isPass	i1
FIELD	798	isGlidingBegin	i1
FIELD	799	isGliding	i1
FIELD	800	ImageWH	struct(CGPoint)
FIELD	808	nowPos	struct(CGPoint)
FIELD	816	startPos	struct(CGPoint)
FIELD	824	endPos	struct(CGPoint)
FIELD	832	moveStep	i4
FIELD	836	moveY	f4
FIELD	840	moveScale	f4
FIELD	844	nowScale	f4
FIELD	848	moveAlpha	i4
FIELD	852	nowAlpha	i4
FIELD	856	timer	i4
FIELD	860	timer_dmg	i4
FIELD	864	timer_hit	i4
FIELD	868	timer_appear	i4
FIELD	872	timer_broken	i4
FIELD	876	posz	f4
IVARVAR	0x72018	RavenSlider	sliderNo	24
IVARVAR	0x7201c	RavenSlider	WeaponData	28
IVARVAR	0x72020	RavenSlider	isDisp	792
IVARVAR	0x72024	RavenSlider	isDammage	793
IVARVAR	0x72028	RavenSlider	isEscape	794
IVARVAR	0x7202c	RavenSlider	isBroken	795
IVARVAR	0x72030	RavenSlider	isHead	796
IVARVAR	0x72034	RavenSlider	isPass	797
IVARVAR	0x72038	RavenSlider	isGlidingBegin	798
IVARVAR	0x7203c	RavenSlider	isGliding	799
IVARVAR	0x72040	RavenSlider	ImageWH	800
IVARVAR	0x72044	RavenSlider	nowPos	808
IVARVAR	0x72048	RavenSlider	startPos	816
IVARVAR	0x7204c	RavenSlider	endPos	824
IVARVAR	0x72050	RavenSlider	moveStep	832
IVARVAR	0x72054	RavenSlider	moveY	836
IVARVAR	0x72058	RavenSlider	moveScale	840
IVARVAR	0x7205c	RavenSlider	nowScale	844
IVARVAR	0x72060	RavenSlider	moveAlpha	848
IVARVAR	0x72064	RavenSlider	nowAlpha	852
IVARVAR	0x72068	RavenSlider	timer	856
IVARVAR	0x7206c	RavenSlider	timer_dmg	860
IVARVAR	0x72070	RavenSlider	timer_hit	864
IVARVAR	0x72074	RavenSlider	timer_appear	868
IVARVAR	0x72078	RavenSlider	timer_broken	872
IVARVAR	0x7207c	RavenSlider	posz	876
CLASS	RavenBomb	1572	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	WeaponData	struct(EneDat)
FIELD	788	MissileImage	struct(CrashLandingAppDelegate_tex_Gitai)
FIELD	836	SmokeImages	arr(12,struct(CrashLandingAppDelegate_tex_Gitai))
FIELD	1412	pRpgExplosion	ptr(struct(EneDat_eff_char))
FIELD	1416	pBomb	arr(30,id)
FIELD	1536	isHit	i1
FIELD	1540	imgGroup	i4
FIELD	1544	imgIndex	i4
FIELD	1548	anmMissile	i4
FIELD	1552	frmMissile	i4
FIELD	1556	frmMissileMax	i4
FIELD	1560	bomb_cnt	i4
FIELD	1564	bomb_accel	i4
FIELD	1568	posz	f4
IVARVAR	0x72460	RavenBomb	WeaponData	24
IVARVAR	0x72464	RavenBomb	MissileImage	788
IVARVAR	0x72468	RavenBomb	SmokeImages	836
IVARVAR	0x7246c	RavenBomb	pRpgExplosion	1412
IVARVAR	0x72470	RavenBomb	pBomb	1416
IVARVAR	0x72474	RavenBomb	isHit	1536
IVARVAR	0x72478	RavenBomb	imgGroup	1540
IVARVAR	0x7247c	RavenBomb	imgIndex	1544
IVARVAR	0x72480	RavenBomb	anmMissile	1548
IVARVAR	0x72484	RavenBomb	frmMissile	1552
IVARVAR	0x72488	RavenBomb	frmMissileMax	1556
IVARVAR	0x7248c	RavenBomb	bomb_cnt	1560
IVARVAR	0x72490	RavenBomb	bomb_accel	1564
IVARVAR	0x72494	RavenBomb	posz	1568
CLASS	ClusterBomb	80	
FIELD	4	ImageWH	struct(CGPoint)
FIELD	12	img_group	i4
FIELD	16	img_index	i4
FIELD	20	img_anime	i4
FIELD	24	img_frame	i4
FIELD	28	img_frame_max	i4
FIELD	32	bomb_no	i4
FIELD	36	bomb_timer	i4
FIELD	40	bomb_frame	i4
FIELD	44	bomb_frame_max	i4
FIELD	48	img_scale	f4
FIELD	52	bomb_scale	f4
FIELD	56	posX	f4
FIELD	60	posY	f4
FIELD	64	moveX	f4
FIELD	68	moveY	f4
FIELD	72	isDisp	i1
FIELD	73	isBomb	i1
FIELD	74	isEnd	i1
FIELD	76	timer	i4
IVARVAR	0x72498	ClusterBomb	ImageWH	4
IVARVAR	0x7249c	ClusterBomb	img_group	12
IVARVAR	0x724a0	ClusterBomb	img_index	16
IVARVAR	0x724a4	ClusterBomb	img_anime	20
IVARVAR	0x724a8	ClusterBomb	img_frame	24
IVARVAR	0x724ac	ClusterBomb	img_frame_max	28
IVARVAR	0x724b0	ClusterBomb	bomb_no	32
IVARVAR	0x724b4	ClusterBomb	bomb_timer	36
IVARVAR	0x724b8	ClusterBomb	bomb_frame	40
IVARVAR	0x724bc	ClusterBomb	bomb_frame_max	44
IVARVAR	0x724c0	ClusterBomb	img_scale	48
IVARVAR	0x724c4	ClusterBomb	bomb_scale	52
IVARVAR	0x724c8	ClusterBomb	posX	56
IVARVAR	0x724cc	ClusterBomb	posY	60
IVARVAR	0x724d0	ClusterBomb	moveX	64
IVARVAR	0x724d4	ClusterBomb	moveY	68
IVARVAR	0x724d8	ClusterBomb	isDisp	72
IVARVAR	0x724dc	ClusterBomb	isBomb	73
IVARVAR	0x724e0	ClusterBomb	isEnd	74
IVARVAR	0x724e4	ClusterBomb	timer	76
CLASS	Wolf	300	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	appearWolf	i1
FIELD	53	isStageChange	i1
FIELD	54	isReversal	i1
FIELD	55	isBodyAttack	i1
FIELD	56	isBodyAttackHit	i1
FIELD	57	isBodyAttackSpring	i1
FIELD	60	havenCntComing	i4
FIELD	64	havenCntMax	i4
FIELD	68	isRailgunShot	i1
FIELD	72	railgunWait	i4
FIELD	76	railgunCharge	i4
FIELD	80	isOpen	i1
FIELD	81	isAttack	i1
FIELD	82	isDamage	i1
FIELD	83	isGauge	i1
FIELD	84	isLeftMove	i1
FIELD	88	damageHit	i4
FIELD	92	timeStage	i4
FIELD	96	isPointAppear	arr(7,i1)
FIELD	104	summonHaven	arr(21,i4)
FIELD	188	summonHavenNext	arr(21,i4)
FIELD	272	alphaAppear	i4
FIELD	276	alphaAppearAdd	i4
FIELD	280	itemAppear	i4
FIELD	284	typeHit	i4
FIELD	288	timeWait	i4
FIELD	292	pRailgun	id
FIELD	296	successionHP	ptr(i4)
IVARVAR	0x728b0	Wolf	appearWolf	52
IVARVAR	0x728b4	Wolf	isStageChange	53
IVARVAR	0x728b8	Wolf	isReversal	54
IVARVAR	0x728bc	Wolf	isBodyAttack	55
IVARVAR	0x728c0	Wolf	isBodyAttackHit	56
IVARVAR	0x728c4	Wolf	isBodyAttackSpring	57
IVARVAR	0x728c8	Wolf	havenCntComing	60
IVARVAR	0x728cc	Wolf	havenCntMax	64
IVARVAR	0x728d0	Wolf	isRailgunShot	68
IVARVAR	0x728d4	Wolf	railgunWait	72
IVARVAR	0x728d8	Wolf	railgunCharge	76
IVARVAR	0x728dc	Wolf	isOpen	80
IVARVAR	0x728e0	Wolf	isAttack	81
IVARVAR	0x728e4	Wolf	isDamage	82
IVARVAR	0x728e8	Wolf	isGauge	83
IVARVAR	0x728ec	Wolf	isLeftMove	84
IVARVAR	0x728f0	Wolf	damageHit	88
IVARVAR	0x728f4	Wolf	timeStage	92
IVARVAR	0x728f8	Wolf	isPointAppear	96
IVARVAR	0x728fc	Wolf	summonHaven	104
IVARVAR	0x72900	Wolf	summonHavenNext	188
IVARVAR	0x72904	Wolf	alphaAppear	272
IVARVAR	0x72908	Wolf	alphaAppearAdd	276
IVARVAR	0x7290c	Wolf	itemAppear	280
IVARVAR	0x72910	Wolf	typeHit	284
IVARVAR	0x72914	Wolf	timeWait	288
IVARVAR	0x72918	Wolf	pRailgun	292
IVARVAR	0x7291c	Wolf	successionHP	296
CLASS	Ray	208	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	appearRay	i1
FIELD	56	startHp	i4
FIELD	60	isHP80	i1
FIELD	61	isHP60	i1
FIELD	62	isFirst	i1
FIELD	63	isDamage	i1
FIELD	64	isAttack	i1
FIELD	65	isHit	i1
FIELD	66	isDraw	i1
FIELD	67	isLanding	i1
FIELD	68	isExtra	i1
FIELD	69	isDemoFlag	i1
FIELD	72	cntChecker	i4
FIELD	76	cntLockOn	i4
FIELD	80	damageHit	i4
FIELD	84	isStageChange	i1
FIELD	88	appearPointOld	i4
FIELD	92	appearPointNext	i4
FIELD	96	distancePoint	i4
FIELD	100	distancePointOld	i4
FIELD	104	weapon	i4
FIELD	108	weaponWait	i4
FIELD	112	weaponCount	i4
FIELD	116	weaponDamage	i4
FIELD	120	weaponTimer	i4
FIELD	124	alphaAppear	i4
FIELD	128	frmEffAppear	i4
FIELD	132	frmEffAppearMax	i4
FIELD	136	frmEffJump	i4
FIELD	140	frmEffFall	i4
FIELD	144	originX	f4
FIELD	148	originY	f4
FIELD	152	originScale	f4
FIELD	156	addScale	f4
FIELD	160	fallScale	f4
FIELD	164	typeHit	i4
FIELD	168	timeWait	i4
FIELD	172	timeJump	i4
FIELD	176	timeCnt	i4
FIELD	180	pMissile	arr(5,id)
FIELD	200	pWeapon	id
FIELD	204	successionHP	ptr(i4)
IVARVAR	0x72f04	Ray	appearRay	52
IVARVAR	0x72f08	Ray	startHp	56
IVARVAR	0x72f0c	Ray	isHP80	60
IVARVAR	0x72f10	Ray	isHP60	61
IVARVAR	0x72f14	Ray	isFirst	62
IVARVAR	0x72f18	Ray	isDamage	63
IVARVAR	0x72f1c	Ray	isAttack	64
IVARVAR	0x72f20	Ray	isHit	65
IVARVAR	0x72f24	Ray	isDraw	66
IVARVAR	0x72f28	Ray	isLanding	67
IVARVAR	0x72f2c	Ray	isExtra	68
IVARVAR	0x72f30	Ray	isDemoFlag	69
IVARVAR	0x72f34	Ray	cntChecker	72
IVARVAR	0x72f38	Ray	cntLockOn	76
IVARVAR	0x72f3c	Ray	damageHit	80
IVARVAR	0x72f40	Ray	isStageChange	84
IVARVAR	0x72f44	Ray	appearPointOld	88
IVARVAR	0x72f48	Ray	appearPointNext	92
IVARVAR	0x72f4c	Ray	distancePoint	96
IVARVAR	0x72f50	Ray	distancePointOld	100
IVARVAR	0x72f54	Ray	weapon	104
IVARVAR	0x72f58	Ray	weaponWait	108
IVARVAR	0x72f5c	Ray	weaponCount	112
IVARVAR	0x72f60	Ray	weaponDamage	116
IVARVAR	0x72f64	Ray	weaponTimer	120
IVARVAR	0x72f68	Ray	alphaAppear	124
IVARVAR	0x72f6c	Ray	frmEffAppear	128
IVARVAR	0x72f70	Ray	frmEffAppearMax	132
IVARVAR	0x72f74	Ray	frmEffJump	136
IVARVAR	0x72f78	Ray	frmEffFall	140
IVARVAR	0x72f7c	Ray	originX	144
IVARVAR	0x72f80	Ray	originY	148
IVARVAR	0x72f84	Ray	originScale	152
IVARVAR	0x72f88	Ray	addScale	156
IVARVAR	0x72f8c	Ray	fallScale	160
IVARVAR	0x72f90	Ray	typeHit	164
IVARVAR	0x72f94	Ray	timeWait	168
IVARVAR	0x72f98	Ray	timeJump	172
IVARVAR	0x72f9c	Ray	timeCnt	176
IVARVAR	0x72fa0	Ray	pMissile	180
IVARVAR	0x72fa4	Ray	pWeapon	200
IVARVAR	0x72fa8	Ray	successionHP	204
CLASS	Mantis	168	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	appearMantis	i1
FIELD	53	isFirst	i1
FIELD	54	isReaver	i1
FIELD	56	alphaAppear	i4
FIELD	60	actionInterval	i4
FIELD	64	actionIntervalBonus	i4
FIELD	68	timeWait	i4
FIELD	72	warpInterval	i4
FIELD	76	warpAfterStep	i4
FIELD	80	damageSE	i4
FIELD	84	successionHP	ptr(i4)
FIELD	88	originalY	f4
FIELD	92	havenSoldierCount	i4
FIELD	96	havenSoldierIndexTop	i4
FIELD	100	havenSoldierIndexRandom	i4
FIELD	104	havenSoldiersAreSummoned	u1
FIELD	105	requestSummonHavenSoldiers	u1
FIELD	108	summonTimer	i4
FIELD	112	summonIndex	i4
FIELD	116	dollTimer	arr(2,i4)
FIELD	124	didLookDown	arr(2,u1)
FIELD	128	doll	arr(2,id)
FIELD	136	dollResurrectTime	i4
FIELD	140	dollTakeAwayTime	i4
FIELD	144	willTakeTheDollOver	u1
FIELD	145	lookDownMantisDoll	u1
FIELD	148	karambitCount	i4
FIELD	152	karambit	arr(4,id)
IVARVAR	0x733ec	Mantis	appearMantis	52
IVARVAR	0x733f0	Mantis	isFirst	53
IVARVAR	0x733f4	Mantis	isReaver	54
IVARVAR	0x733f8	Mantis	alphaAppear	56
IVARVAR	0x733fc	Mantis	actionInterval	60
IVARVAR	0x73400	Mantis	actionIntervalBonus	64
IVARVAR	0x73404	Mantis	timeWait	68
IVARVAR	0x73408	Mantis	warpInterval	72
IVARVAR	0x7340c	Mantis	warpAfterStep	76
IVARVAR	0x73410	Mantis	damageSE	80
IVARVAR	0x73414	Mantis	successionHP	84
IVARVAR	0x73418	Mantis	originalY	88
IVARVAR	0x7341c	Mantis	havenSoldierCount	92
IVARVAR	0x73420	Mantis	havenSoldierIndexTop	96
IVARVAR	0x73424	Mantis	havenSoldierIndexRandom	100
IVARVAR	0x73428	Mantis	havenSoldiersAreSummoned	104
IVARVAR	0x7342c	Mantis	requestSummonHavenSoldiers	105
IVARVAR	0x73430	Mantis	summonTimer	108
IVARVAR	0x73434	Mantis	summonIndex	112
IVARVAR	0x73438	Mantis	dollTimer	116
IVARVAR	0x7343c	Mantis	didLookDown	124
IVARVAR	0x73440	Mantis	doll	128
IVARVAR	0x73444	Mantis	dollResurrectTime	136
IVARVAR	0x73448	Mantis	dollTakeAwayTime	140
IVARVAR	0x7344c	Mantis	willTakeTheDollOver	144
IVARVAR	0x73450	Mantis	lookDownMantisDoll	145
IVARVAR	0x73454	Mantis	karambitCount	148
IVARVAR	0x73458	Mantis	karambit	152
CLASS	Liquid	132	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	percentGuard	i4
FIELD	56	isGuard	i1
FIELD	57	isGuardOfSnake	i1
FIELD	58	isDamage	i1
FIELD	59	isAttack	i1
FIELD	60	isChain	i1
FIELD	61	isDucking	i1
FIELD	62	isFlagDemo	i1
FIELD	63	isChainOfSnake	i1
FIELD	64	cntChainOfSnake	i4
FIELD	68	typeAttack	i4
FIELD	72	stepAttack	i4
FIELD	76	stepAttackHit	i4
FIELD	80	attackFlag	i4
FIELD	84	cntDamage	i4
FIELD	88	cntAnime	i4
FIELD	92	timeGuard	i4
FIELD	96	timeStiffening	i4
FIELD	100	timeWait	i4
FIELD	104	timeLast	i4
FIELD	108	statusPlayer	i4
FIELD	112	successionHP	ptr(i4)
FIELD	116	guard_shake	f4
FIELD	120	snake_chance	i4
FIELD	124	is_snake_chance	i1
FIELD	128	attackStep	i4
IVARVAR	0x73844	Liquid	percentGuard	52
IVARVAR	0x73848	Liquid	isGuard	56
IVARVAR	0x7384c	Liquid	isGuardOfSnake	57
IVARVAR	0x73850	Liquid	isDamage	58
IVARVAR	0x73854	Liquid	isAttack	59
IVARVAR	0x73858	Liquid	isChain	60
IVARVAR	0x7385c	Liquid	isDucking	61
IVARVAR	0x73860	Liquid	isFlagDemo	62
IVARVAR	0x73864	Liquid	isChainOfSnake	63
IVARVAR	0x73868	Liquid	cntChainOfSnake	64
IVARVAR	0x7386c	Liquid	typeAttack	68
IVARVAR	0x73870	Liquid	stepAttack	72
IVARVAR	0x73874	Liquid	stepAttackHit	76
IVARVAR	0x73878	Liquid	attackFlag	80
IVARVAR	0x7387c	Liquid	cntDamage	84
IVARVAR	0x73880	Liquid	cntAnime	88
IVARVAR	0x73884	Liquid	timeGuard	92
IVARVAR	0x73888	Liquid	timeStiffening	96
IVARVAR	0x7388c	Liquid	timeWait	100
IVARVAR	0x73890	Liquid	timeLast	104
IVARVAR	0x73894	Liquid	statusPlayer	108
IVARVAR	0x73898	Liquid	successionHP	112
IVARVAR	0x7389c	Liquid	guard_shake	116
IVARVAR	0x738a0	Liquid	snake_chance	120
IVARVAR	0x738a4	Liquid	is_snake_chance	124
IVARVAR	0x738a8	Liquid	attackStep	128
CLASS	HavenSoldierB	56	HavenSoldier
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	moveDestination	i2
FIELD	54	originalAppearPoint	i2
IVARVAR	0x73b14	HavenSoldierB	moveDestination	52
IVARVAR	0x73b18	HavenSoldierB	originalAppearPoint	54
CLASS	DwarfGekko	104	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	anime_offset	i4
FIELD	56	isLeader	u1
FIELD	60	groupMemberCount	i4
FIELD	64	groupAppearPoints	u8
FIELD	72	groupCannotAppear	u1
FIELD	76	dyingMoveTimer	i4
FIELD	80	dyingMoveScale	f4
FIELD	84	dyingMovePos	struct(CGPoint)
FIELD	92	groupMember	arr(2,id)
FIELD	100	leader	id
IVARVAR	0x73f00	DwarfGekko	anime_offset	52
IVARVAR	0x73f04	DwarfGekko	isLeader	56
IVARVAR	0x73f08	DwarfGekko	groupMemberCount	60
IVARVAR	0x73f0c	DwarfGekko	groupAppearPoints	64
IVARVAR	0x73f10	DwarfGekko	groupCannotAppear	72
IVARVAR	0x73f14	DwarfGekko	dyingMoveTimer	76
IVARVAR	0x73f18	DwarfGekko	dyingMoveScale	80
IVARVAR	0x73f1c	DwarfGekko	dyingMovePos	84
IVARVAR	0x73f20	DwarfGekko	groupMember	92
IVARVAR	0x73f24	DwarfGekko	leader	100
CLASS	SelfDestructionGekko	128	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
FIELD	52	moveDestination	i2
FIELD	54	originalAppearPoint	i2
FIELD	56	effectPlasmaLoopStep	i4
FIELD	60	effectPlasmaLoopCount	i4
FIELD	64	effectLightIsVisible	u1
FIELD	65	effectPlasmaIsVisible	u1
FIELD	68	effectLightTimer	i4
FIELD	72	effectPlasmaTimer	i4
FIELD	76	landEffect	struct(Canard_windBlastEffect)
IVARVAR	0x741d0	SelfDestructionGekko	moveDestination	52
IVARVAR	0x741d4	SelfDestructionGekko	originalAppearPoint	54
IVARVAR	0x741d8	SelfDestructionGekko	effectPlasmaLoopStep	56
IVARVAR	0x741dc	SelfDestructionGekko	effectPlasmaLoopCount	60
IVARVAR	0x741e0	SelfDestructionGekko	effectLightIsVisible	64
IVARVAR	0x741e4	SelfDestructionGekko	effectPlasmaIsVisible	65
IVARVAR	0x741e8	SelfDestructionGekko	effectLightTimer	68
IVARVAR	0x741ec	SelfDestructionGekko	effectPlasmaTimer	72
IVARVAR	0x741f0	SelfDestructionGekko	landEffect	76
CLASS	Railgun	128	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	index	i2
FIELD	28	imgGroup	i4
FIELD	32	imgIndex	i4
FIELD	36	anmCharge	i4
FIELD	40	frmCharge	i4
FIELD	44	frmChargeMax	i4
FIELD	48	anmAtk	i4
FIELD	52	frmAtk	i4
FIELD	56	frmAtkMax	i4
FIELD	60	anmRay	i4
FIELD	64	frmRay	i4
FIELD	68	frmRayMax	i4
FIELD	72	rotRay	f4
FIELD	76	alphaRay	i4
FIELD	80	pRpgExplosion	ptr(struct(EneDat_eff_char))
FIELD	84	isActive	i1
FIELD	85	isShot	i1
FIELD	86	isCancel	i1
FIELD	87	isHit	i1
FIELD	88	scaleRailgun	f4
FIELD	92	scaleRailgunX	f4
FIELD	96	scaleRailgunY	f4
FIELD	100	addx	f4
FIELD	104	addy	f4
FIELD	108	rayx	f4
FIELD	112	rayy	f4
FIELD	116	posx	f4
FIELD	120	posy	f4
FIELD	124	posz	f4
IVARVAR	0x744f8	Railgun	index	24
IVARVAR	0x744fc	Railgun	imgGroup	28
IVARVAR	0x74500	Railgun	imgIndex	32
IVARVAR	0x74504	Railgun	anmCharge	36
IVARVAR	0x74508	Railgun	frmCharge	40
IVARVAR	0x7450c	Railgun	frmChargeMax	44
IVARVAR	0x74510	Railgun	anmAtk	48
IVARVAR	0x74514	Railgun	frmAtk	52
IVARVAR	0x74518	Railgun	frmAtkMax	56
IVARVAR	0x7451c	Railgun	anmRay	60
IVARVAR	0x74520	Railgun	frmRay	64
IVARVAR	0x74524	Railgun	frmRayMax	68
IVARVAR	0x74528	Railgun	rotRay	72
IVARVAR	0x7452c	Railgun	alphaRay	76
IVARVAR	0x74530	Railgun	pRpgExplosion	80
IVARVAR	0x74534	Railgun	isActive	84
IVARVAR	0x74538	Railgun	isShot	85
IVARVAR	0x7453c	Railgun	isCancel	86
IVARVAR	0x74540	Railgun	isHit	87
IVARVAR	0x74544	Railgun	scaleRailgun	88
IVARVAR	0x74548	Railgun	scaleRailgunX	92
IVARVAR	0x7454c	Railgun	scaleRailgunY	96
IVARVAR	0x74550	Railgun	addx	100
IVARVAR	0x74554	Railgun	addy	104
IVARVAR	0x74558	Railgun	rayx	108
IVARVAR	0x7455c	Railgun	rayy	112
IVARVAR	0x74560	Railgun	posx	116
IVARVAR	0x74564	Railgun	posy	120
IVARVAR	0x74568	Railgun	posz	124
CLASS	RayMissile	152	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	missileNo	i4
FIELD	28	imgGroup	i4
FIELD	32	imgIndex	i4
FIELD	36	frmBullet	i4
FIELD	40	frmBulletMax	i4
FIELD	44	rotBullet	f4
FIELD	48	frmJet1Max	i4
FIELD	52	frmJet2Max	i4
FIELD	56	frmJet3Max	i4
FIELD	60	frmJetTail	i4
FIELD	64	frmJetTailMax	i4
FIELD	68	frmBomb	i4
FIELD	72	frmBombMax	i4
FIELD	76	scaleBulletAdd	f4
FIELD	80	scaleBullet	f4
FIELD	84	scaleStart	f4
FIELD	88	timer	i4
FIELD	92	timeWait	i4
FIELD	96	timeCount	i4
FIELD	100	isActive	i1
FIELD	101	isShot	i1
FIELD	102	isJet	i1
FIELD	103	isBomb	i1
FIELD	104	isHit	i1
FIELD	105	isBroken	i1
FIELD	106	isEnd	i1
FIELD	108	movex	f4
FIELD	112	movey	f4
FIELD	116	jetx	f4
FIELD	120	jety	f4
FIELD	124	jetx2	f4
FIELD	128	jety2	f4
FIELD	132	startx	f4
FIELD	136	starty	f4
FIELD	140	posx	f4
FIELD	144	posy	f4
FIELD	148	posz	f4
IVARVAR	0x74960	RayMissile	missileNo	24
IVARVAR	0x74964	RayMissile	imgGroup	28
IVARVAR	0x74968	RayMissile	imgIndex	32
IVARVAR	0x7496c	RayMissile	frmBullet	36
IVARVAR	0x74970	RayMissile	frmBulletMax	40
IVARVAR	0x74974	RayMissile	rotBullet	44
IVARVAR	0x74978	RayMissile	frmJet1Max	48
IVARVAR	0x7497c	RayMissile	frmJet2Max	52
IVARVAR	0x74980	RayMissile	frmJet3Max	56
IVARVAR	0x74984	RayMissile	frmJetTail	60
IVARVAR	0x74988	RayMissile	frmJetTailMax	64
IVARVAR	0x7498c	RayMissile	frmBomb	68
IVARVAR	0x74990	RayMissile	frmBombMax	72
IVARVAR	0x74994	RayMissile	scaleBulletAdd	76
IVARVAR	0x74998	RayMissile	scaleBullet	80
IVARVAR	0x7499c	RayMissile	scaleStart	84
IVARVAR	0x749a0	RayMissile	timer	88
IVARVAR	0x749a4	RayMissile	timeWait	92
IVARVAR	0x749a8	RayMissile	timeCount	96
IVARVAR	0x749ac	RayMissile	isActive	100
IVARVAR	0x749b0	RayMissile	isShot	101
IVARVAR	0x749b4	RayMissile	isJet	102
IVARVAR	0x749b8	RayMissile	isBomb	103
IVARVAR	0x749bc	RayMissile	isHit	104
IVARVAR	0x749c0	RayMissile	isBroken	105
IVARVAR	0x749c4	RayMissile	isEnd	106
IVARVAR	0x749c8	RayMissile	movex	108
IVARVAR	0x749cc	RayMissile	movey	112
IVARVAR	0x749d0	RayMissile	jetx	116
IVARVAR	0x749d4	RayMissile	jety	120
IVARVAR	0x749d8	RayMissile	jetx2	124
IVARVAR	0x749dc	RayMissile	jety2	128
IVARVAR	0x749e0	RayMissile	startx	132
IVARVAR	0x749e4	RayMissile	starty	136
IVARVAR	0x749e8	RayMissile	posx	140
IVARVAR	0x749ec	RayMissile	posy	144
IVARVAR	0x749f0	RayMissile	posz	148
CLASS	Doll	140	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	dollType	i4
FIELD	28	nodes	arr(2,struct(CGPoint))
FIELD	44	nodeVelocities	arr(2,struct(CGPoint))
FIELD	60	lastScale	f4
FIELD	64	ground	struct(CGPoint)
FIELD	72	velocity	f4
FIELD	76	img_group	i4
FIELD	80	img_index	i4
FIELD	84	anime_top	i4
FIELD	88	anime_no	i4
FIELD	92	anime_cnt	i4
FIELD	96	anime_update	u1
FIELD	100	distance	i4
FIELD	104	alpha	i4
FIELD	108	maxHP	i4
FIELD	112	HP	i4
FIELD	116	hitTimer	i4
FIELD	120	step	i4
FIELD	124	fallStep	i4
FIELD	128	warpStep	i4
FIELD	132	swingTimer	i4
FIELD	136	swingScale	f4
IVARVAR	0x74cfc	Doll	dollType	24
IVARVAR	0x74d00	Doll	nodes	28
IVARVAR	0x74d04	Doll	nodeVelocities	44
IVARVAR	0x74d08	Doll	lastScale	60
IVARVAR	0x74d0c	Doll	ground	64
IVARVAR	0x74d10	Doll	velocity	72
IVARVAR	0x74d14	Doll	img_group	76
IVARVAR	0x74d18	Doll	img_index	80
IVARVAR	0x74d1c	Doll	anime_top	84
IVARVAR	0x74d20	Doll	anime_no	88
IVARVAR	0x74d24	Doll	anime_cnt	92
IVARVAR	0x74d28	Doll	anime_update	96
IVARVAR	0x74d2c	Doll	distance	100
IVARVAR	0x74d30	Doll	alpha	104
IVARVAR	0x74d34	Doll	maxHP	108
IVARVAR	0x74d38	Doll	HP	112
IVARVAR	0x74d3c	Doll	hitTimer	116
IVARVAR	0x74d40	Doll	step	120
IVARVAR	0x74d44	Doll	fallStep	124
IVARVAR	0x74d48	Doll	warpStep	128
IVARVAR	0x74d4c	Doll	swingTimer	132
IVARVAR	0x74d50	Doll	swingScale	136
CLASS	Karambit	114	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	pos	struct(CGPoint)
FIELD	32	posz	f4
FIELD	36	velocity	struct(CGPoint)
FIELD	44	acceleration	struct(CGPoint)
FIELD	52	startY	f4
FIELD	56	startScale	f4
FIELD	60	lastScale	f4
FIELD	64	startPosition	i4
FIELD	68	img_group	i4
FIELD	72	img_index	i4
FIELD	76	anime_cnt	i4
FIELD	80	alpha	i4
FIELD	84	timer	i4
FIELD	88	hitTimer	i4
FIELD	92	waitTime	i4
FIELD	96	standbyTime	i4
FIELD	100	SEinterval	i4
FIELD	104	distance	i4
FIELD	108	step	i4
FIELD	112	isVisible	u1
FIELD	113	didGiveDamage	u1
IVARVAR	0x74fdc	Karambit	pos	24
IVARVAR	0x74fe0	Karambit	posz	32
IVARVAR	0x74fe4	Karambit	velocity	36
IVARVAR	0x74fe8	Karambit	acceleration	44
IVARVAR	0x74fec	Karambit	startY	52
IVARVAR	0x74ff0	Karambit	startScale	56
IVARVAR	0x74ff4	Karambit	lastScale	60
IVARVAR	0x74ff8	Karambit	startPosition	64
IVARVAR	0x74ffc	Karambit	img_group	68
IVARVAR	0x75000	Karambit	img_index	72
IVARVAR	0x75004	Karambit	anime_cnt	76
IVARVAR	0x75008	Karambit	alpha	80
IVARVAR	0x7500c	Karambit	timer	84
IVARVAR	0x75010	Karambit	hitTimer	88
IVARVAR	0x75014	Karambit	waitTime	92
IVARVAR	0x75018	Karambit	standbyTime	96
IVARVAR	0x7501c	Karambit	SEinterval	100
IVARVAR	0x75020	Karambit	distance	104
IVARVAR	0x75024	Karambit	step	108
IVARVAR	0x75028	Karambit	isVisible	112
IVARVAR	0x7502c	Karambit	didGiveDamage	113
CLASS	FBomb	244	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	data	struct(FBomb_data)
FIELD	36	current	struct(FBomb_data)
FIELD	48	next	struct(FBomb_data)
FIELD	60	posz	f4
FIELD	64	blur	arr(12,struct(FBomb_data))
FIELD	208	img_group	i4
FIELD	212	img_index	i4
FIELD	216	index	i4
FIELD	220	target	i4
FIELD	224	timer	i4
FIELD	228	interval	i4
FIELD	232	isVisible	u1
FIELD	236	pRpgExplosion	ptr(struct(EneDat_eff_char))
FIELD	240	distance	i4
IVARVAR	0x75270	FBomb	data	24
IVARVAR	0x75274	FBomb	current	36
IVARVAR	0x75278	FBomb	next	48
IVARVAR	0x7527c	FBomb	posz	60
IVARVAR	0x75280	FBomb	blur	64
IVARVAR	0x75284	FBomb	img_group	208
IVARVAR	0x75288	FBomb	img_index	212
IVARVAR	0x7528c	FBomb	index	216
IVARVAR	0x75290	FBomb	target	220
IVARVAR	0x75294	FBomb	timer	224
IVARVAR	0x75298	FBomb	interval	228
IVARVAR	0x7529c	FBomb	isVisible	232
IVARVAR	0x752a0	FBomb	pRpgExplosion	236
IVARVAR	0x752a4	FBomb	distance	240
CLASS	RayWeapon	52	WeaponBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	type	i4
FIELD	16	pEneDat	ptr(struct(EneDat))
FIELD	20	damage	i4
FIELD	24	modeWeapon	i4
FIELD	28	isShot	i1
FIELD	29	isActive	i1
FIELD	30	isHighMode	i1
FIELD	32	timer	i4
FIELD	36	scaleEnemy	f4
FIELD	40	posx	f4
FIELD	44	posy	f4
FIELD	48	posz	f4
IVARVAR	0x75410	RayWeapon	modeWeapon	24
IVARVAR	0x75414	RayWeapon	isShot	28
IVARVAR	0x75418	RayWeapon	isActive	29
IVARVAR	0x7541c	RayWeapon	isHighMode	30
IVARVAR	0x75420	RayWeapon	timer	32
IVARVAR	0x75424	RayWeapon	scaleEnemy	36
IVARVAR	0x75428	RayWeapon	posx	40
IVARVAR	0x7542c	RayWeapon	posy	44
IVARVAR	0x75430	RayWeapon	posz	48
CLASS	NPC	52	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
CLASS	HavenSoldier	52	EnemyBase
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
CLASS	HavenSoldierA	52	HavenSoldier
FIELD	4	_type	i4
FIELD	8	z	ptr(f4)
FIELD	12	pEneDat	ptr(struct(EneDat))
FIELD	16	pStatus	ptr(struct(EnemyBase_pStatus))
FIELD	20	timer	i4
FIELD	24	index	i2
FIELD	26	appear	i2
FIELD	28	sign	i2
FIELD	30	attack	i2
FIELD	32	move	i2
FIELD	34	aiControl	i2
FIELD	36	aiStep	i2
FIELD	38	attackTime	i2
FIELD	40	fade	u1
FIELD	42	limit	i2
FIELD	44	didHitMissile	u1
FIELD	45	didDisappeard	u1
FIELD	48	wallHitType	i4
IVARPTR	0x690a8	0x6f5cc
IVARPTR	0x690ac	0x6f5c0
IVARPTR	0x690b0	0x71328
IVARPTR	0x690b4	0x6f5d4
IVARPTR	0x690b8	0x6f5e0
IVARPTR	0x690bc	0x6f5d0
IVARPTR	0x690c0	0x6f5dc
IVARPTR	0x690c4	0x6f5d8
IVARPTR	0x690d0	0x6f5fc
IVARPTR	0x690d4	0x6f5e4
IVARPTR	0x690d8	0x6f5c8
IVARPTR	0x690dc	0x6f5c4
IVARPTR	0x690e0	0x6f5e8
IVARPTR	0x690e4	0x6f5ec
IVARPTR	0x690e8	0x6f5f8
IVARPTR	0x690f8	0x70674
IVARPTR	0x690fc	0x7066c
IVARPTR	0x69100	0x70670
IVARPTR	0x69104	0x71324
METHOD	Texture2D	-	contentSize	0x2741	struct(CGSize)	id	sel
METHOD	Texture2D	-	pixelFormat	0x2735	i4	id	sel
METHOD	Texture2D	-	name	0x2729	u4	id	sel
METHOD	Texture2D	-	maxS	0x271d	f4	id	sel
METHOD	Texture2D	-	maxT	0x2711	f4	id	sel
METHOD	Texture2D	-	description	0x29f9	id	id	sel
METHOD	Texture2D	-	dealloc	0x2ca1	void	id	sel
METHOD	Texture2D	-	initWithData:pixelFormat:pixelsWide:pixelsHigh:contentSize:	0x2a91	id	id	sel	ptr(void)	i4	u4	u4	struct(CGSize)
METHOD	Texture2D	-	setClamp:	0x2705	void	id	sel	i1
METHOD	Texture2D	+	initialize	0x2c35	void	id	sel
METHOD	DWconnect	+	ConvertDataNSNumber::	0x425f	i4	id	sel	id	i4
METHOD	DWconnect	+	ConvertDataNSArray::	0x42a5	id	id	sel	id	id
METHOD	DWconnect	+	DataRead::	0x42ed	id	id	sel	id	id
METHOD	DWconnect	+	DataConnect	0x425d	void	id	sel
METHOD	DWconnect	+	DWWebTo:	0x4331	void	id	sel	id
METHOD	DWWebView	-	dealloc	0x4379	void	id	sel
METHOD	DWWebView	-	webView:didFailLoadWithError:	0x439d	void	id	sel	id	id
METHOD	DWWebView	-	webViewDidFinishLoad:	0x4421	void	id	sel	id
METHOD	DWWebView	-	webViewDidStartLoad:	0x4449	void	id	sel	id
METHOD	DWWebView	-	closeWebView	0x4471	void	id	sel
METHOD	DWWebView	-	openWebView:url:	0x4485	void	id	sel	id	id
METHOD	DWWebView	-	initWithFrame:	0x44f9	id	id	sel	struct(CGRect)
METHOD	CrashLandingAppDelegate	-	drebin_drawAnnounce_side	0x4ce9	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_drawAnnounce	0x4ead	void	id	sel
METHOD	CrashLandingAppDelegate	-	drawLoadingAct:	0x5069	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	drawAdvice	0x50dd	void	id	sel
METHOD	CrashLandingAppDelegate	-	draw_dp_resalt::::	0x5309	void	id	sel	i4	f4	f4	f4
METHOD	CrashLandingAppDelegate	-	sh_drawResult_Failed	0x1dd7d	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_drawResult_Clear	0x1aca5	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_drawResult	0xa8a5	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_drawFadeForChangingBG	0x8b15	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_drawClearCondition	0x1be71	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_drawInterface	0x8ed5	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_drawMain	0x10a95	void	id	sel
METHOD	CrashLandingAppDelegate	-	drawHistory	0x1c4f5	void	id	sel
METHOD	CrashLandingAppDelegate	-	story_draw	0x1c9c5	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_drawBuymenu	0xbf5d	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_drawView	0x5639	void	id	sel
METHOD	CrashLandingAppDelegate	-	draw_Dp:::::	0x56b5	void	id	sel	i4	f4	f4	f4	i4
METHOD	CrashLandingAppDelegate	-	drebin_drawBar	0x583d	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_drawBottommenu	0x5f61	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_drawBackground	0xc791	void	id	sel
METHOD	CrashLandingAppDelegate	-	drawManual	0x1cf19	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_drawHelptxt	0x1d2c9	void	id	sel
METHOD	CrashLandingAppDelegate	-	updateAnimeColor	0x4c8d	void	id	sel
METHOD	CrashLandingAppDelegate	-	GetAnimColorNext:	0x6165	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	GetAnimColorBack	0x4c45	i4	id	sel
METHOD	CrashLandingAppDelegate	-	GetAnimColorBlink	0x61b5	i4	id	sel
METHOD	CrashLandingAppDelegate	-	GetAnimColorBlink:	0x4bed	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	GetAnimColor:	0x4bd7	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	title_drawHelp	0x9f11	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_drawBar	0x1d5c5	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_drawLogo	0x61c9	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_drawBackground	0x1e385	void	id	sel
METHOD	CrashLandingAppDelegate	-	DrawGame	0x1e569	void	id	sel
METHOD	CrashLandingAppDelegate	-	GameScene	0x10f2d	void	id	sel
METHOD	CrashLandingAppDelegate	-	getStringWidth:::	0x867d	i4	id	sel	ptr(i1)	i4	i4
METHOD	CrashLandingAppDelegate	-	wordWrap::	0x62c1	i4	id	sel	ptr(i1)	i4
METHOD	CrashLandingAppDelegate	-	wordWrapCheck:	0x635d	i4	id	sel	ptr(i1)
METHOD	CrashLandingAppDelegate	-	checkAlphabet::	0x4b41	i4	id	sel	ptr(i1)	i1
METHOD	CrashLandingAppDelegate	-	GetAutoLineFeedText:::	0x10701	id	id	sel	id	i4	i4
METHOD	CrashLandingAppDelegate	-	checkKana:	0x4b0b	i4	id	sel	ptr(i1)
METHOD	CrashLandingAppDelegate	-	checkMoji:	0x4a91	i4	id	sel	ptr(i1)
METHOD	CrashLandingAppDelegate	-	bottomNGwordCheck::	0x109a1	i4	id	sel	ptr(i1)	i1
METHOD	CrashLandingAppDelegate	-	topNGwordCheck:	0x10a21	i4	id	sel	ptr(i1)
METHOD	CrashLandingAppDelegate	-	Hyphenation:::	0x10799	i4	id	sel	ptr(i1)	i4	i4
METHOD	CrashLandingAppDelegate	-	AutoLineFeed:::	0x10899	void	id	sel	ptr(i1)	i4	i4
METHOD	CrashLandingAppDelegate	-	title_manual_is_inspect	0x4a65	i1	id	sel
METHOD	CrashLandingAppDelegate	-	title_manual_set_inspect:	0xa155	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	title_manual_is_next	0x4a39	i1	id	sel
METHOD	CrashLandingAppDelegate	-	title_manual_is_back	0x4a0d	i1	id	sel
METHOD	CrashLandingAppDelegate	-	title_manual_view_main	0xa9f1	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_manual_main	0x63a1	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_manual_release	0x64c5	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_manual_load:	0x13469	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Credit_Main	0xac7d	void	id	sel
METHOD	CrashLandingAppDelegate	-	Credit_Release	0x6515	void	id	sel
METHOD	CrashLandingAppDelegate	-	Credit_Load	0x136b1	void	id	sel
METHOD	CrashLandingAppDelegate	-	option_release	0xf009	void	id	sel
METHOD	CrashLandingAppDelegate	-	option_load	0x137dd	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_option_main	0x104f5	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_radio_main	0x6569	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_movie_main	0x65b5	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_history_view_main	0xae71	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_history_main	0x6601	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_history_release	0x142cd	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_history_load:	0x143dd	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Get_StoryBgmNo:	0x4a01	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Get_StringLinestr:::	0x10ddd	id	id	sel	id	i4	i4
METHOD	CrashLandingAppDelegate	-	Get_StringLineNum:	0x10ead	i4	id	sel	id
METHOD	CrashLandingAppDelegate	-	GetStoryText:	0x6725	id	id	sel	i4
METHOD	CrashLandingAppDelegate	-	story_release	0x6751	void	id	sel
METHOD	CrashLandingAppDelegate	-	story_main	0xb189	void	id	sel
METHOD	CrashLandingAppDelegate	-	story_load	0x14641	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_announce_main	0xb4bd	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_announce_release	0x67f5	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_announce_load	0x14ca5	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_announce_skip	0xa1a9	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_is_announce::	0x4991	i1	id	sel	i1	i4
METHOD	CrashLandingAppDelegate	-	drebin_is_announce:	0x6859	i1	id	sel	i1
METHOD	CrashLandingAppDelegate	-	getMovieURL:	0x498d	id	id	sel	i4
METHOD	CrashLandingAppDelegate	-	getWPName:thum:	0x6875	id	id	sel	i4	bool
METHOD	CrashLandingAppDelegate	-	get_WPNum:	0x4965	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	GetTouch_Purchase	0x871d	u1	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_movie	0xb641	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_view	0xb6f5	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_buy	0xc989	void	id	sel
METHOD	CrashLandingAppDelegate	-	Drebin_AnimControl	0x14f61	void	id	sel
METHOD	CrashLandingAppDelegate	-	Drebin_Touch	0x152cd	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_DataLoad	0xd32d	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_release	0xf249	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_main	0xb7a1	void	id	sel
METHOD	CrashLandingAppDelegate	-	drebin_load	0x158fd	void	id	sel
METHOD	CrashLandingAppDelegate	-	Menu_Touch:	0xfc05	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	GetMenuNum:	0x4911	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Title_AnimControl	0x4745	void	id	sel
METHOD	CrashLandingAppDelegate	-	Change_scene:	0x16c69	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Get_TitleTouch_Logo	0x8795	u1	id	sel
METHOD	CrashLandingAppDelegate	-	Get_TitleTouch_Help	0x87ed	u1	id	sel
METHOD	CrashLandingAppDelegate	-	Get_TitleTouch_Back	0x8845	u1	id	sel
METHOD	CrashLandingAppDelegate	-	title_loadMenuData	0xd895	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_bg_move	0x68bd	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_release	0xf4cd	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_shoot_stage_select	0x69e9	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_shoot_mode_select	0x6a35	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_main	0x6a81	void	id	sel
METHOD	CrashLandingAppDelegate	-	title_load	0x16e79	void	id	sel
METHOD	CrashLandingAppDelegate	-	createTexWithText:fontSize:	0x183f9	id	id	sel	id	f4
METHOD	CrashLandingAppDelegate	-	sh_procDrum	0x6acd	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_checkHitDrum:rect:	0x6bcd	u1	id	sel	i4	struct(CGRect)
METHOD	CrashLandingAppDelegate	-	sh_hitCheckWithExplosion	0x6e01	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_getExplosionRectScale::	0x4729	f4	id	sel	i4	i4
METHOD	CrashLandingAppDelegate	-	ReturnStageGame:	0xa4dd	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Load	0xcc85	void	id	sel
METHOD	CrashLandingAppDelegate	-	LoadSet::::::::::	0xf9c9	void	id	sel	ptr(i1)	i4	i4	i4	i4	i4	struct(CGSize)	i4	id	f4
METHOD	CrashLandingAppDelegate	-	LoadSet::::::	0xfaad	void	id	sel	ptr(i1)	i4	i4	i4	i4	i4
METHOD	CrashLandingAppDelegate	-	ReleasePack	0xf8ed	void	id	sel
METHOD	CrashLandingAppDelegate	-	StageObjLoad	0x7369	void	id	sel
METHOD	CrashLandingAppDelegate	-	GitaiLoad	0x7551	void	id	sel
METHOD	CrashLandingAppDelegate	-	game_start_release	0x75b1	void	id	sel
METHOD	CrashLandingAppDelegate	-	game_start_load	0x18495	void	id	sel
METHOD	CrashLandingAppDelegate	-	ImageLoad	0x7629	void	id	sel
METHOD	CrashLandingAppDelegate	-	SoundLoad	0x779d	void	id	sel
METHOD	CrashLandingAppDelegate	-	ALRL_Load::	0xcf35	void	id	sel	i4	id
METHOD	CrashLandingAppDelegate	-	getNextStageBG:random:	0xba31	i4	id	sel	i4	u1
METHOD	CrashLandingAppDelegate	-	LoadChange	0x18809	void	id	sel
METHOD	CrashLandingAppDelegate	-	TouchLoop	0x78b5	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_release_enemy	0x78dd	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_release	0x7a79	void	id	sel
METHOD	CrashLandingAppDelegate	-	setMimicObjects	0x889d	void	id	sel
METHOD	CrashLandingAppDelegate	-	setStageObjects	0x89b5	void	id	sel
METHOD	CrashLandingAppDelegate	-	releaseStageData	0xf725	void	id	sel
METHOD	CrashLandingAppDelegate	-	loadStageData	0xdcc1	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_initgame	0xd00d	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_load_enemy:	0x7cf5	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	sh_load_enemy_setting	0x7db9	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_load	0x18eb5	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_procClearCondition	0xb8d1	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_procResult	0x19f1d	void	id	sel
METHOD	CrashLandingAppDelegate	-	sh_gameMain	0xbb3d	void	id	sel
METHOD	CrashLandingAppDelegate	-	startGameBGM	0xa7c9	void	id	sel
METHOD	CrashLandingAppDelegate	-	Draw_Fade	0x1e24d	void	id	sel
METHOD	CrashLandingAppDelegate	-	Fade_Set:	0x46c9	void	id	sel	i4
METHOD	CrashLandingAppDelegate	-	Fade_Control	0x4635	void	id	sel
METHOD	CrashLandingAppDelegate	-	GetFigue:	0x4615	i4	id	sel	i4
METHOD	CrashLandingAppDelegate	-	LocalizeString:	0x812d	id	id	sel	i4
METHOD	CrashLandingAppDelegate	-	myMovieFinishedCallback:	0xa809	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	playMovieAtURL:	0xa731	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	applicationDidReceiveMemoryWarning:	0xa4cd	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	applicationDidBecomeActive:	0xa489	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	applicationWillResignActive:	0xa459	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	accelerometer:didAccelerate:	0x81d9	void	id	sel	id	id
METHOD	CrashLandingAppDelegate	-	ReturnDiaLogResult	0x45fd	i4	id	sel
METHOD	CrashLandingAppDelegate	-	initDiaLog::::	0x84f5	void	id	sel	id	id	id	id
METHOD	CrashLandingAppDelegate	-	alertView:clickedButtonAtIndex:	0x45f1	void	id	sel	id	i4
METHOD	CrashLandingAppDelegate	-	renderScene	0xa2c1	void	id	sel
METHOD	CrashLandingAppDelegate	-	dealloc	0xa20d	void	id	sel
METHOD	CrashLandingAppDelegate	-	applicationWillTerminate:	0x8561	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	applicationDidFinishLaunching:	0x1a5a9	void	id	sel	id
METHOD	CrashLandingAppDelegate	-	initAccelero	0x8581	void	id	sel
METHOD	CrashLandingAppDelegate	+	initialize	0x10d15	void	id	sel
METHOD	SoundThread	-	exec	0x21f2d	void	id	sel
METHOD	SoundThread	-	exit	0x21eb1	void	id	sel
METHOD	SoundThread	-	init:	0x21ee9	void	id	sel	ptr(struct(SoundService))
METHOD	TableReader	+	maxLineNum:	0x22015	i4	id	sel	id
METHOD	TableReader	+	lineData:lineRange:newLocation:	0x2206d	id	id	sel	id	struct(_NSRange)	ptr(u4)
METHOD	TableReader	+	readFile:	0x21ff1	id	id	sel	id
METHOD	DWGraphics	-	dealloc	0x22275	void	id	sel
METHOD	DWGraphics	-	DelLoad	0x22455	void	id	sel
METHOD	DWGraphics	-	DrawLoad:	0x22c19	void	id	sel	f4
METHOD	DWGraphics	-	Loadset:	0x22a9b	void	id	sel	i4
METHOD	DWGraphics	-	delfillRect:	0x224a5	void	id	sel	i4
METHOD	DWGraphics	-	fillRect::	0x22645	void	id	sel	i4	struct(CGPoint)
METHOD	DWGraphics	-	LoadfillRect::	0x224c5	void	id	sel	struct(CGRect)	i4
METHOD	DWGraphics	-	delString:	0x22559	void	id	sel	i4
METHOD	DWGraphics	-	GetdrawString:	0x221d9	id	id	sel	i4
METHOD	DWGraphics	-	drawString::	0x226a5	void	id	sel	i4	struct(CGPoint)
METHOD	DWGraphics	-	LoadString::	0x22585	void	id	sel	id	i4
METHOD	DWGraphics	-	setColor:fr:fg:fb:	0x221a9	void	id	sel	f4	f4	f4	f4
METHOD	DWGraphics	-	setColor:ir:ig:ib:	0x2214d	void	id	sel	f4	i4	i4	i4
METHOD	DWGraphics	-	setColor:	0x220d5	void	id	sel	i4
METHOD	DWGraphics	-	finalize	0x22299	void	id	sel
METHOD	DWGraphics	-	init	0x222bd	id	id	sel
METHOD	DWGraphics	+	releaseBitmapData:	0x22a81	void	id	sel	ptr(struct(tagBMPDATA))
METHOD	DWGraphics	+	getPaletteRGB:index:	0x22271	i4	id	sel	ptr(struct(tagBMPDATA))	i4
METHOD	DWGraphics	+	getPaletteB:index:	0x22335	i4	id	sel	ptr(struct(tagBMPDATA))	i4
METHOD	DWGraphics	+	getPaletteG:index:	0x22349	i4	id	sel	ptr(struct(tagBMPDATA))	i4
METHOD	DWGraphics	+	getPaletteR:index:	0x22361	i4	id	sel	ptr(struct(tagBMPDATA))	i4
METHOD	DWGraphics	+	getColorIndex:x:y:	0x221e9	i4	id	sel	ptr(struct(tagBMPDATA))	i4	i4
METHOD	DWGraphics	+	getColorRGB:x:y:	0x22379	i4	id	sel	ptr(struct(tagBMPDATA))	i4	i4
METHOD	DWGraphics	+	getColorB:x:y:	0x223f9	i4	id	sel	ptr(struct(tagBMPDATA))	i4	i4
METHOD	DWGraphics	+	getColorG:x:y:	0x22415	i4	id	sel	ptr(struct(tagBMPDATA))	i4	i4
METHOD	DWGraphics	+	getColorR:x:y:	0x22435	i4	id	sel	ptr(struct(tagBMPDATA))	i4	i4
METHOD	DWGraphics	+	loadBitmapData:	0x22979	struct(tagBMPDATA)	id	sel	id
METHOD	DWGraphics	+	Set_TexEnvf_Color_NoFade:	0x22705	void	id	sel	i4
METHOD	DWGraphics	+	Retrun_TexEnvf_Color	0x2276d	void	id	sel
METHOD	DWGraphics	+	Add_TexEnvf_Color:	0x227d5	void	id	sel	i4
METHOD	DWGraphics	+	Set_TexEnvf_Color:	0x22911	void	id	sel	i4
METHOD	DWUtilities	+	getPackImageWH::::	0x22f85	struct(CGPoint)	id	sel	i4	i4	i4	i4
METHOD	DWUtilities	+	readShort:	0x233b5	i2	id	sel	ptr(struct(__sFILE))
METHOD	DWUtilities	+	getMaxFrame::	0x22f5d	i2	id	sel	i4	i4
METHOD	DWUtilities	+	getKomaData:::	0x22ee5	ptr(struct(DWUtilities_getKomaData_a0))	id	sel	i4	i4	i4
METHOD	DWUtilities	+	releaseAnimeData:	0x23315	void	id	sel	i4
METHOD	DWUtilities	+	readAnimeData::	0x2302d	void	id	sel	i4	ptr(i1)
METHOD	DWUtilities	+	rlDataAtIndex:	0x22ed5	ptr(struct(DWUtilities_rlDataAtIndex_a0))	id	sel	i4
METHOD	DWUtilities	+	getItemData::::	0x22e81	ptr(struct(DWUtilities_getItemData_a0))	id	sel	i4	i4	i4	i4
METHOD	DWUtilities	+	getItemNun:::	0x22e41	i4	id	sel	i4	i4	i4
METHOD	DWUtilities	+	getPartsData:::	0x22e21	ptr(struct(DWUtilities_getItemData_a0))	id	sel	i4	i4	i4
METHOD	DWUtilities	+	getPartsNun::	0x22e0d	i4	id	sel	i4	i4
METHOD	DWUtilities	+	releaseRectData:	0x23365	void	id	sel	i4
METHOD	DWUtilities	+	readRectData::	0x23191	void	id	sel	i4	ptr(i1)
METHOD	Effect	+	drawEnemyEffectSlide:	0x26815	void	id	sel	ptr(struct(Canard_windBlastEffect))
METHOD	Effect	+	drawEnemyEffectWindBlast:	0x26a69	void	id	sel	ptr(struct(Canard_windBlastEffect))
METHOD	Effect	+	drawEnemyEffectLand:	0x26cc1	void	id	sel	ptr(struct(Canard_windBlastEffect))
METHOD	Effect	+	drawEnemyEffectJump:	0x26f59	void	id	sel	ptr(struct(Canard_windBlastEffect))
METHOD	Effect	+	procEnemyEffect:::::	0x241c5	void	id	sel	ptr(struct(Canard_windBlastEffect))	f4	f4	f4	f4
METHOD	Effect	+	procEnemyEffect::::	0x241e9	void	id	sel	ptr(struct(Canard_windBlastEffect))	f4	f4	f4
METHOD	Effect	+	procEnemyEffect:	0x241a3	void	id	sel	ptr(struct(Canard_windBlastEffect))
METHOD	Effect	+	setEnemyEffect::::::::	0x24211	void	id	sel	ptr(struct(Canard_windBlastEffect))	f4	f4	f4	u4	u1	i4	i4
METHOD	Effect	+	setEnemyEffect:::::::	0x24265	void	id	sel	ptr(struct(Canard_windBlastEffect))	f4	f4	f4	u4	u1	i4
METHOD	Effect	+	setEnemyEffect::::::	0x24295	void	id	sel	ptr(struct(Canard_windBlastEffect))	f4	f4	f4	u4	u1
METHOD	Effect	+	initEnemyEffect:	0x2419d	void	id	sel	ptr(struct(Canard_windBlastEffect))
METHOD	Effect	+	drawGroundHit	0x2815d	void	id	sel
METHOD	Effect	+	procGroundHit	0x2416d	void	id	sel
METHOD	Effect	+	setGroundHit::::	0x28ab9	void	id	sel	f4	f4	f4	i4
METHOD	Effect	+	initGroundHit	0x24151	void	id	sel
METHOD	Effect	+	getSpecialDamageData:	0x24139	ptr(struct(Effect_getSpecialDamageData_a0))	id	sel	i4
METHOD	Effect	+	drawSpecialDamage:	0x28481	void	id	sel	i4
METHOD	Effect	+	procSpecialDamage	0x242c5	void	id	sel
METHOD	Effect	+	setSpecialDamage:::::::	0x28a71	void	id	sel	i4	f4	f4	f4	f4	i4	u4
METHOD	Effect	+	initSpecialDamage	0x2411d	void	id	sel
METHOD	Effect	+	drawEffItemIcon:	0x25975	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	drawEffItem:	0x27135	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	procEffItem:	0x27ded	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	setEffItem:index:type:	0x24325	void	id	sel	ptr(struct(EneDat_eff_char))	ptr(void)	i4
METHOD	Effect	+	clearExplode:	0x240f5	void	id	sel	i4
METHOD	Effect	+	setExplode:scale:len:dmg:link:rect:	0x24451	void	id	sel	struct(CGPoint)	f4	i4	i4	i4	ptr(struct(CGRect))
METHOD	Effect	+	getExpScale:	0x240dd	f4	id	sel	i4
METHOD	Effect	+	addExpLink:num:	0x24079	void	id	sel	i4	i4
METHOD	Effect	+	checkExpLink:num:	0x24045	u1	id	sel	i4	i4
METHOD	Effect	+	setExpLink:	0x24021	i4	id	sel	i4
METHOD	Effect	+	initExpLink	0x23ffd	void	id	sel
METHOD	Effect	+	getEffData:	0x23fe5	ptr(struct(Effect_getEffData_a0))	id	sel	i4
METHOD	Effect	+	stopEffDataSE::	0x23fcd	void	id	sel	i4	i4
METHOD	Effect	+	drawEffData:	0x244b9	void	id	sel	i4
METHOD	Effect	+	procEffData	0x28979	void	id	sel
METHOD	Effect	+	setEffData:x:y:z:scale:delay:se:len:dmg:link:	0x25cdd	i4	id	sel	i4	f4	f4	f4	f4	i4	i4	i4	i4	i4
METHOD	Effect	+	setEffData:x:y:z:scale:delay:se:	0x244e1	i4	id	sel	i4	f4	f4	f4	f4	i4	i4
METHOD	Effect	+	initEffData	0x24515	void	id	sel
METHOD	Effect	+	setEnemyWaitMeterColor::::::	0x23e99	u4	id	sel	ptr(i4)	ptr(f4)	ptr(i4)	ptr(struct(EneDat_waitEff))	u4	i4
METHOD	Effect	+	drawEnemyWaitMeter:x:y:scale:color:	0x286cd	void	id	sel	i4	f4	f4	f4	i4
METHOD	Effect	+	drawWaitEffect::	0x245c5	void	id	sel	ptr(struct(EneDat_waitEff))	ptr(struct(EneDat))
METHOD	Effect	+	porcWaitEffect:	0x27ff1	void	id	sel	ptr(struct(EneDat))
METHOD	Effect	+	setWaitEffect:type:timer:signTime:attackTime:	0x24ae5	void	id	sel	ptr(struct(EneDat))	i4	i4	i2	i2
METHOD	Effect	+	drawEffEnemyHP:::	0x2738d	void	id	sel	ptr(struct(EneDat_eff_char))	i4	i4
METHOD	Effect	+	procEffEnemyHP:	0x24bc9	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	setEffEnemyHP:index:type:	0x24c25	void	id	sel	ptr(struct(EneDat_eff_char))	ptr(void)	i4
METHOD	Effect	+	OffSetXY::	0x23e05	void	id	sel	ptr(struct(EneDat))	ptr(struct(DWUtilities_getKomaData_a0))
METHOD	Effect	+	drawEffEnemyChar:scale:	0x24c8d	void	id	sel	ptr(struct(EneDat_eff_char))	f4
METHOD	Effect	+	drawEffEnemyChar:scale:horizontalReversing:	0x276f1	void	id	sel	ptr(struct(EneDat_eff_char))	f4	i1
METHOD	Effect	+	procEffEnemyChar:	0x25685	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	setEffEnemyChar:index:type:	0x24cb1	void	id	sel	ptr(struct(EneDat_eff_char))	ptr(void)	i4
METHOD	Effect	+	drawEffAnime:	0x265e1	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	procEffAnime:	0x25491	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	setEffAnime:index:type:	0x254e5	void	id	sel	ptr(struct(EneDat_eff_char))	ptr(void)	i4
METHOD	Effect	+	procEffect:	0x23d49	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	setEffect:	0x23ccb	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	procEffAnimeData:	0x23c6d	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	setEffAnimeState:state:	0x23c69	void	id	sel	ptr(struct(EneDat_eff_char))	i4
METHOD	Effect	+	setEffAnimeImage:img:	0x23c65	void	id	sel	ptr(struct(EneDat_eff_char))	ptr(id)
METHOD	Effect	+	setEffAnimeData:img:pat:max:speed:	0x23c43	void	id	sel	ptr(struct(EneDat_eff_char))	ptr(id)	ptr(i4)	i4	f4
METHOD	Effect	+	setEffDrawPos:x:y:scale:	0x23c31	void	id	sel	ptr(struct(EneDat_eff_char))	f4	f4	f4
METHOD	Effect	+	setEffDrawPos:x:y:z:ratio:addx:addy:	0x23bf5	void	id	sel	ptr(struct(EneDat_eff_char))	f4	f4	f4	f4	f4	f4
METHOD	Effect	+	initDrawData:	0x23b91	void	id	sel	ptr(struct(EneDat_eff_char))
METHOD	Effect	+	release	0x25535	void	id	sel
METHOD	Effect	+	reset	0x25575	void	id	sel
METHOD	Effect	+	initWithParameter:	0x255ad	void	id	sel	ptr(struct(EneDat))
METHOD	TextureManager	+	StringdrawImage2:x:y:scale:rot:	0x291f9	void	id	sel	id	f4	f4	f4	i4
METHOD	TextureManager	+	StringdrawImage:x:y:scale:	0x294a9	void	id	sel	id	f4	f4	f4
METHOD	TextureManager	+	drawImage2:x:y:scale:rot:	0x295d5	void	id	sel	id	f4	f4	f4	i4
METHOD	TextureManager	+	setClip2::::	0x28da5	void	id	sel	f4	f4	f4	f4
METHOD	TextureManager	+	drawClipImage:::::::::::	0x28e55	struct(CGPoint)	id	sel	i4	f4	f4	f4	f4	f4	f4	f4	f4	f4	i4
METHOD	TextureManager	+	drawAnimeImage::::::::::	0x29245	struct(CGPoint)	id	sel	i4	i4	f4	f4	i4	i4	f4	f4	f4	i4
METHOD	TextureManager	+	drawImageClipWithID:x:y:scaleW:scaleH:rot:	0x28f71	void	id	sel	i4	f4	f4	f4	f4	i4
METHOD	TextureManager	+	drawImageWithID:x:y:scaleW:scaleH:rot:	0x28fa1	void	id	sel	i4	f4	f4	f4	f4	i4
METHOD	TextureManager	+	drawImageWithID:x:y:scale:rot:	0x28fd1	void	id	sel	i4	f4	f4	f4	i4
METHOD	TextureManager	+	drawImageWithID:x:y:scale:	0x28ffd	void	id	sel	i4	f4	f4	f4
METHOD	TextureManager	+	drawTexture::	0x2902d	void	id	sel	i4	struct(CGPoint)
METHOD	TextureManager	+	drawImageClip:x:y:scaleW:scaleH:rot:	0x29869	void	id	sel	id	f4	f4	f4	f4	i4
METHOD	TextureManager	+	drawImage:x:y:scaleW:scaleH:rot:	0x2938d	void	id	sel	id	f4	f4	f4	f4	i4
METHOD	TextureManager	+	drawImage:x:y:scale:rot:	0x29059	void	id	sel	id	f4	f4	f4	i4
METHOD	TextureManager	+	drawImage:x:y:scale:	0x2907d	void	id	sel	id	f4	f4	f4
METHOD	TextureManager	+	clearImgClip	0x28d99	void	id	sel
METHOD	TextureManager	+	setImgClip::::	0x28d69	void	id	sel	f4	f4	f4	f4
METHOD	TextureManager	+	setClip::::	0x28ca5	void	id	sel	f4	f4	f4	f4
METHOD	TextureManager	+	getTexturePtr:	0x28c95	ptr(id)	id	sel	i4
METHOD	TextureManager	+	getTexture:	0x28c89	id	id	sel	i4
METHOD	TextureManager	+	releaseTexture:	0x290a1	void	id	sel	i4
METHOD	TextureManager	+	loadRectTexture::::::	0x290c5	void	id	sel	i4	struct(CGSize)	f4	f4	f4	f4
METHOD	TextureManager	+	loadTextureAsA8:name:ofType:	0x29119	void	id	sel	i4	id	id
METHOD	TextureManager	+	loadTexture:name:ofType:	0x29151	void	id	sel	i4	id	id
METHOD	TextureManager	+	initialize	0x29189	void	id	sel
METHOD	PMC	-	switchToPMC_B	0x29c5d	void	id	sel
METHOD	PMC	-	switchToPMC_A	0x29bfd	void	id	sel
METHOD	PMC	-	checkPMC_B	0x2a0a1	void	id	sel
METHOD	PMC	-	changeAnimation	0x29cbd	u1	id	sel
METHOD	PMC	-	updateDie	0x29d41	void	id	sel
METHOD	PMC	-	updateAttackPostProcess	0x29db9	void	id	sel
METHOD	PMC	-	updateAttackProcess	0x29e11	void	id	sel
METHOD	PMC	-	updateAttackPreProcess	0x29f9d	void	id	sel
METHOD	PMC	-	initAppearance	0x2a009	void	id	sel
METHOD	PMC	-	dealloc	0x29e89	void	id	sel
METHOD	PMC	-	activate	0x29ec5	u1	id	sel
METHOD	PMC	-	initWithParameter:index:rpgExplosion:	0x29ef9	id	id	sel	ptr(struct(EneDat))	i2	ptr(struct(EneDat_eff_char))
METHOD	NPC	-	getEnemyScale	0x2a129	f4	id	sel
METHOD	NPC	-	changeAnimation	0x2a36d	u1	id	sel
METHOD	NPC	-	copyEnemyInfo::	0x2a139	void	id	sel	i4	i4
METHOD	NPC	-	checkCollisionWithExplosion::	0x2a7cd	i4	id	sel	ptr(struct(CGRect))	i4
METHOD	NPC	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x2a8a5	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	NPC	-	checkCollisionWithBullet:hit:distance:	0x2a3d1	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	NPC	-	renderGauge	0x2a421	void	id	sel
METHOD	NPC	-	render	0x2a299	void	id	sel
METHOD	NPC	-	update:	0x2a4d5	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	NPC	-	activate	0x2a725	u1	id	sel
METHOD	NPC	-	reset	0x2a459	void	id	sel
METHOD	NPC	-	initWithParameter:index:	0x2a2e9	id	id	sel	ptr(struct(EneDat))	i2
METHOD	HavenSoldier	-	calculateDamage:::::	0x2aa25	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	HavenSoldier	-	deadSound:	0x2a985	void	id	sel	u1
METHOD	HavenSoldier	-	attackSound	0x2a9d1	void	id	sel
METHOD	EnemyManager	+	removeItem:	0x2ab41	void	id	sel	i4
METHOD	EnemyManager	+	setItem:enemyType:itemType:	0x2abb1	void	id	sel	i4	i4	i4
METHOD	EnemyManager	+	setItem:enemyType:	0x2c575	void	id	sel	i4	i4
METHOD	EnemyManager	+	getRate:	0x2ac25	i4	id	sel	ptr(struct(CrashLandingAppDelegate_npc_condition))
METHOD	EnemyManager	+	checkItem::	0x2c619	u1	id	sel	i4	u1
METHOD	EnemyManager	+	checkNPC:	0x2c711	u1	id	sel	i4
METHOD	EnemyManager	+	takeover	0x2aca1	void	id	sel
METHOD	EnemyManager	+	updateAppearData:	0x2adad	u1	id	sel	i4
METHOD	EnemyManager	+	shortCutTime:	0x2aec9	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	EnemyManager	+	clearCheck:	0x2afc5	void	id	sel	ptr(struct(EnemyManager_clearCheck_a3))
METHOD	EnemyManager	+	updatePattern	0x2b0c1	void	id	sel
METHOD	EnemyManager	+	updateEachCharacter:	0x2c0a9	void	id	sel	ptr(struct(EnemyManager_clearCheck_a3))
METHOD	EnemyManager	+	updateRespawnRequest	0x2b1f5	void	id	sel
METHOD	EnemyManager	+	updateSpawnRequest	0x2b305	void	id	sel
METHOD	EnemyManager	+	release	0x2b609	void	id	sel
METHOD	EnemyManager	+	itemFlag	0x2ab35	u8	id	sel
METHOD	EnemyManager	+	getItem:::	0x2b669	void	id	sel	i4	ptr(struct(CGPoint))	f4
METHOD	EnemyManager	+	clearItemFlag:	0x2aae1	void	id	sel	i4
METHOD	EnemyManager	+	searchWeapon:	0x2ba41	id	id	sel	i4
METHOD	EnemyManager	+	addWeapon:	0x2b68d	void	id	sel	id
METHOD	EnemyManager	+	checkOverlappedEnemy::	0x2baf5	u1	id	sel	i4	id
METHOD	EnemyManager	+	npc	0x2aad5	id	id	sel
METHOD	EnemyManager	+	enemyOfType:	0x2bc99	id	id	sel	i4
METHOD	EnemyManager	+	enemyAtIndex:	0x2b6bd	id	id	sel	i4
METHOD	EnemyManager	+	add:	0x2b6d9	void	id	sel	id
METHOD	EnemyManager	+	setFlags:	0x2aac5	void	id	sel	u4
METHOD	EnemyManager	+	clearFlags:	0x2aab5	void	id	sel	u4
METHOD	EnemyManager	+	checkFlags:	0x2aaa1	u1	id	sel	u4
METHOD	EnemyManager	+	checkMissionComplete	0x2aa95	u1	id	sel
METHOD	EnemyManager	+	renderItemIcon	0x2b6f5	void	id	sel
METHOD	EnemyManager	+	renderGauge	0x2bd4d	void	id	sel
METHOD	EnemyManager	+	render	0x2be09	void	id	sel
METHOD	EnemyManager	+	update:	0x2b711	void	id	sel	ptr(struct(EnemyManager_clearCheck_a3))
METHOD	EnemyManager	+	reset	0x2bead	void	id	sel
METHOD	EnemyManager	+	initWithParameter:npcData:itemData:npc:	0x2b849	void	id	sel	ptr(struct(EneDat))	ptr(struct(CrashLandingAppDelegate_npc))	ptr(struct(CrashLandingAppDelegate_item))	ptr(struct(EneDat))
METHOD	EnemyBase	-	subDamage:	0x2cc7d	void	id	sel	i4
METHOD	EnemyBase	-	getDamage::	0x2e5d1	i4	id	sel	i4	i4
METHOD	EnemyBase	-	caluclateDamageWithExplosion:	0x2e52d	i4	id	sel	i4
METHOD	EnemyBase	-	calculateDamage:::::	0x2e2e9	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	EnemyBase	-	checkCollisionWithBullet:hit:distance:	0x2ccd5	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	EnemyBase	-	getEnemyScale	0x2cc3d	f4	id	sel
METHOD	EnemyBase	-	setAnimation:	0x2cf75	u1	id	sel	i4
METHOD	EnemyBase	-	setAnimation::	0x2cf91	u1	id	sel	i4	u1
METHOD	EnemyBase	-	setAnimation:::	0x2cfad	u1	id	sel	i4	u1	u1
METHOD	EnemyBase	-	changeAnimation	0x2cbed	u1	id	sel
METHOD	EnemyBase	-	updateAnimationFrame	0x2cb91	void	id	sel
METHOD	EnemyBase	-	updateAnimation	0x2d03d	void	id	sel
METHOD	EnemyBase	-	initPosition:	0x2cb1d	void	id	sel	i4
METHOD	EnemyBase	-	checkCollisionWithPlayer	0x2d0d5	u1	id	sel
METHOD	EnemyBase	-	resetEnemyBase	0x2d18d	void	id	sel
METHOD	EnemyBase	-	deadSound:	0x2e3d5	void	id	sel	u1
METHOD	EnemyBase	-	setGunMuzzleFlash	0x2df9d	void	id	sel
METHOD	EnemyBase	-	attackSound	0x2e41d	void	id	sel
METHOD	EnemyBase	-	attackGun:	0x2d369	void	id	sel	u1
METHOD	EnemyBase	-	attack	0x2d3e1	void	id	sel
METHOD	EnemyBase	-	move	0x2c9e1	u1	id	sel
METHOD	EnemyBase	-	initDie	0x2c9df	void	id	sel
METHOD	EnemyBase	-	initDataMove	0x2c9dd	void	id	sel
METHOD	EnemyBase	-	initSpecialAttack	0x2c9db	void	id	sel
METHOD	EnemyBase	-	initSelfDestruction	0x2c9d9	void	id	sel
METHOD	EnemyBase	-	initLifeAct	0x2c9d7	void	id	sel
METHOD	EnemyBase	-	initMoveEnd	0x2c9d5	void	id	sel
METHOD	EnemyBase	-	initMoveAttack2	0x2c9d3	void	id	sel
METHOD	EnemyBase	-	initMoveAttack	0x2c9d1	void	id	sel
METHOD	EnemyBase	-	initMove	0x2c987	void	id	sel
METHOD	EnemyBase	-	initAttack	0x2c985	void	id	sel
METHOD	EnemyBase	-	initAppearance	0x2d411	void	id	sel
METHOD	EnemyBase	-	updateMovePostProcess	0x2c957	void	id	sel
METHOD	EnemyBase	-	updateMoveProcess	0x2e46d	void	id	sel
METHOD	EnemyBase	-	updateMovePreProcess	0x2c955	void	id	sel
METHOD	EnemyBase	-	updateAttackPostProcess	0x2d459	void	id	sel
METHOD	EnemyBase	-	updateAttackProcess	0x2d47d	void	id	sel
METHOD	EnemyBase	-	updateAttackPreProcess	0x2c953	void	id	sel
METHOD	EnemyBase	-	updateAppearancePostProcess	0x2d491	void	id	sel
METHOD	EnemyBase	-	updateAppearanceProcess	0x2d4a5	void	id	sel
METHOD	EnemyBase	-	updateAppearancePreProcess	0x2c951	void	id	sel
METHOD	EnemyBase	-	updateDie	0x2d559	void	id	sel
METHOD	EnemyBase	-	updateDataMove	0x2c94f	void	id	sel
METHOD	EnemyBase	-	updateSpecialAttack	0x2c94d	void	id	sel
METHOD	EnemyBase	-	updateSelfDestruction	0x2c94b	void	id	sel
METHOD	EnemyBase	-	updateLifeAct	0x2c949	void	id	sel
METHOD	EnemyBase	-	updateMoveEnd	0x2d659	void	id	sel
METHOD	EnemyBase	-	updateMoveAttack2	0x2c947	void	id	sel
METHOD	EnemyBase	-	updateMoveAttack	0x2c945	void	id	sel
METHOD	EnemyBase	-	updateMove	0x2d6a5	void	id	sel
METHOD	EnemyBase	-	updateAttack	0x2d705	void	id	sel
METHOD	EnemyBase	-	updateAppearance	0x2d7c9	void	id	sel
METHOD	EnemyBase	-	setAiControl:	0x2c92d	void	id	sel	i4
METHOD	EnemyBase	-	setNextAction	0x2d831	void	id	sel
METHOD	EnemyBase	-	dealloc	0x2e2c5	void	id	sel
METHOD	EnemyBase	-	isActiveCollision	0x2c909	u1	id	sel
METHOD	EnemyBase	-	hitMissile:	0x2c8fd	void	id	sel	u1
METHOD	EnemyBase	-	didHitMissile	0x2c8f1	u1	id	sel
METHOD	EnemyBase	-	checkCollisionWithEnemy:	0x2d86d	u1	id	sel	id
METHOD	EnemyBase	-	checkCollisionWithExplosion::	0x2da5d	i4	id	sel	ptr(struct(CGRect))	i4
METHOD	EnemyBase	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x2dc3d	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	EnemyBase	-	imageRect:	0x2e20d	void	id	sel	ptr(struct(CGRect))
METHOD	EnemyBase	-	takeover:	0x2dcfd	void	id	sel	id
METHOD	EnemyBase	-	canTakeover	0x2c8d5	u1	id	sel
METHOD	EnemyBase	-	respawnTime	0x2c8c1	i4	id	sel
METHOD	EnemyBase	-	limit	0x2c8b5	i4	id	sel
METHOD	EnemyBase	-	clearFactor	0x2c8a1	i4	id	sel
METHOD	EnemyBase	-	lifespan	0x2c895	i4	id	sel
METHOD	EnemyBase	-	isActivatable	0x2c87d	u1	id	sel
METHOD	EnemyBase	-	ignoreShortCut	0x2c869	u1	id	sel
METHOD	EnemyBase	-	onlyItem	0x2c859	u1	id	sel
METHOD	EnemyBase	-	getPosZ	0x2c849	f4	id	sel
METHOD	EnemyBase	-	getPosY	0x2c839	f4	id	sel
METHOD	EnemyBase	-	getPosX	0x2c829	f4	id	sel
METHOD	EnemyBase	-	getHp	0x2c819	i4	id	sel
METHOD	EnemyBase	-	getEnemyData	0x2c80d	ptr(struct(EneDat))	id	sel
METHOD	EnemyBase	-	getDistance	0x2c7fd	i4	id	sel
METHOD	EnemyBase	-	type	0x2c7ed	i4	id	sel
METHOD	EnemyBase	-	appearPoint	0x2c7dd	i4	id	sel
METHOD	EnemyBase	-	inactivate	0x2c7cd	void	id	sel
METHOD	EnemyBase	-	activate	0x2c76d	u1	id	sel
METHOD	EnemyBase	-	renderGauge	0x2dd29	void	id	sel
METHOD	EnemyBase	-	render	0x2dda9	void	id	sel
METHOD	EnemyBase	-	update:	0x2de11	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	EnemyBase	-	reset	0x2dedd	void	id	sel
METHOD	EnemyBase	-	initWithParameter:index:	0x2def1	id	id	sel	ptr(struct(EneDat))	i2
METHOD	Canard	-	setVelocity:::	0x2f6f5	void	id	sel	f4	f4	u1
METHOD	Canard	-	updateHovering	0x2f4f9	void	id	sel
METHOD	Canard	-	initHovering	0x2e745	void	id	sel
METHOD	Canard	-	resetCanard	0x2e76d	void	id	sel
METHOD	Canard	-	move	0x2e641	u1	id	sel
METHOD	Canard	-	getEnemyScale	0x2e795	f4	id	sel
METHOD	Canard	-	attackSound	0x2ef45	void	id	sel
METHOD	Canard	-	updateDie	0x2e97d	void	id	sel
METHOD	Canard	-	updateMoveEnd	0x2e9d5	void	id	sel
METHOD	Canard	-	initMoveEnd	0x2e601	void	id	sel
METHOD	Canard	-	updateMoveAttack2	0x2f1ad	void	id	sel
METHOD	Canard	-	updateAttackPostProcess	0x2eacd	void	id	sel
METHOD	Canard	-	updateAttackProcess	0x2eb5d	void	id	sel
METHOD	Canard	-	updateAttack	0x2ebd5	void	id	sel
METHOD	Canard	-	updateAppearancePostProcess	0x2f05d	void	id	sel
METHOD	Canard	-	initAppearance	0x2ef51	void	id	sel
METHOD	Canard	-	dealloc	0x2ec09	void	id	sel
METHOD	Canard	-	calculateDamage:::::	0x2ede5	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Canard	-	render	0x2ec45	void	id	sel
METHOD	Canard	-	update:	0x2ec89	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Canard	-	reset	0x2eccd	void	id	sel
METHOD	Canard	-	initWithParameter:index:rpgExplosion:	0x2ed01	id	id	sel	ptr(struct(EneDat))	i2	ptr(struct(EneDat_eff_char))
METHOD	PoweredSuit	-	resetPoweredSuit	0x2f9c5	void	id	sel
METHOD	PoweredSuit	-	calculateDamage:::::	0x2fbbd	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	PoweredSuit	-	deadSound:	0x2fff9	void	id	sel	u1
METHOD	PoweredSuit	-	attackSound	0x2ff81	void	id	sel
METHOD	PoweredSuit	-	updateDie	0x2fe69	void	id	sel
METHOD	PoweredSuit	-	updateAttackPostProcess	0x2fed1	void	id	sel
METHOD	PoweredSuit	-	updateAttack	0x2fa0d	void	id	sel
METHOD	PoweredSuit	-	updateAppearanceProcess	0x2fc69	void	id	sel
METHOD	PoweredSuit	-	initAppearance	0x2fc21	void	id	sel
METHOD	PoweredSuit	-	render	0x2fab5	void	id	sel
METHOD	PoweredSuit	-	update:	0x2faf9	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	PoweredSuit	-	reset	0x2fb3d	void	id	sel
METHOD	PoweredSuit	-	initWithParameter:index:	0x2fb71	id	id	sel	ptr(struct(EneDat))	i2
METHOD	PoweredSuit	+	checkLoopSE:	0x2f97d	u1	id	sel	i4
METHOD	PoweredSuit	+	stopLoopSE:	0x2f91d	u1	id	sel	i4
METHOD	PoweredSuit	+	setLoopSE:	0x2f8cd	u1	id	sel	i4
METHOD	PoweredSuit	+	resetLoopSE	0x2f8bd	void	id	sel
METHOD	Gekko	-	getMovePoint	0x309b5	i4	id	sel
METHOD	Gekko	-	updateMoveRate	0x3021d	void	id	sel
METHOD	Gekko	-	resetMoveRate	0x30309	void	id	sel
METHOD	Gekko	-	resetGekko	0x30375	void	id	sel
METHOD	Gekko	-	getEnemyScale	0x30191	f4	id	sel
METHOD	Gekko	-	attackSound	0x30af9	void	id	sel
METHOD	Gekko	-	changeAnimation	0x31501	u1	id	sel
METHOD	Gekko	-	updateAnimationFrame	0x301d5	void	id	sel
METHOD	Gekko	-	updateDie	0x30425	void	id	sel
METHOD	Gekko	-	updateMove	0x30b25	void	id	sel
METHOD	Gekko	-	initMove	0x30125	void	id	sel
METHOD	Gekko	-	updateAttack	0x30c95	void	id	sel
METHOD	Gekko	-	initAppearance	0x304ad	void	id	sel
METHOD	Gekko	-	caluclateDamageWithExplosion:	0x310ad	i4	id	sel	i4
METHOD	Gekko	-	calculateDamage:::::	0x31139	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Gekko	-	appearPoint	0x30119	i4	id	sel
METHOD	Gekko	-	activate	0x3056d	u1	id	sel
METHOD	Gekko	-	render	0x3079d	void	id	sel
METHOD	Gekko	-	update:	0x307fd	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Gekko	-	reset	0x30859	void	id	sel
METHOD	Gekko	-	initWithParameter:index:	0x3088d	id	id	sel	ptr(struct(EneDat))	i2
METHOD	Gekko	+	getMoveBaseRateNear	0x3010d	i2	id	sel
METHOD	Gekko	+	getMoveBaseRateMiddle	0x30101	i2	id	sel
METHOD	Gekko	+	getMoveBaseRateFar	0x300f5	i2	id	sel
METHOD	Gekko	+	getMoveRateNearCoefficient	0x300e9	i2	id	sel
METHOD	Gekko	+	getMoveRateMiddleCoefficient	0x300dd	i2	id	sel
METHOD	Gekko	+	getMoveRateFarCoefficient	0x300d1	i2	id	sel
METHOD	Gekko	+	resetMoveRateCoefficient	0x3092d	void	id	sel
METHOD	Gekko	+	clearMovablePoint:	0x30095	void	id	sel	i4
METHOD	Gekko	+	setMovablePoint:	0x3005d	void	id	sel	i4
METHOD	Gekko	+	initMovablePoints	0x3004d	void	id	sel
METHOD	Gekko	+	getMovablePoints	0x30041	u8	id	sel
METHOD	Gekko	+	decCount	0x3002d	void	id	sel
METHOD	Gekko	+	incCount	0x3001d	void	id	sel
METHOD	Gekko	+	setCount:	0x30011	void	id	sel	i2
METHOD	Gekko	+	getCount	0x30005	i2	id	sel
METHOD	Octopus	-	resetOctopusAppearPoint	0x321ed	void	id	sel
METHOD	Octopus	-	resetOctopus	0x31a85	void	id	sel
METHOD	Octopus	-	changeAnimation	0x33039	u1	id	sel
METHOD	Octopus	-	updateAnimationFrame	0x31939	void	id	sel
METHOD	Octopus	-	attackSound	0x331d5	void	id	sel
METHOD	Octopus	-	moveSet	0x33221	void	id	sel
METHOD	Octopus	-	updateDie	0x3197d	void	id	sel
METHOD	Octopus	-	updateMove	0x31b39	void	id	sel
METHOD	Octopus	-	initMove	0x31c35	void	id	sel
METHOD	Octopus	-	updateAttack	0x3267d	void	id	sel
METHOD	Octopus	-	updateAppearanceProcess	0x31c49	void	id	sel
METHOD	Octopus	-	updateAppearance	0x31d71	void	id	sel
METHOD	Octopus	-	initAppearance	0x32e4d	void	id	sel
METHOD	Octopus	-	dealloc	0x31de1	void	id	sel
METHOD	Octopus	-	calculateDamage:::::	0x32909	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Octopus	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x319e5	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Octopus	-	checkCollisionWithBullet:hit:distance:	0x31a35	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	Octopus	-	update:	0x31e7d	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Octopus	-	reset	0x31fa5	void	id	sel
METHOD	Octopus	-	initWithParameter:index:hp:gitai:rpgExplosion:	0x31fd9	id	id	sel	ptr(struct(EneDat))	i2	ptr(i4)	ptr(struct(CrashLandingAppDelegate_tex_Gitai))	ptr(struct(EneDat_eff_char))
METHOD	Octopus	+	canPutFBombs	0x32179	u1	id	sel
METHOD	Octopus	+	getChangeBGCount	0x3192d	i4	id	sel
METHOD	Octopus	+	incChangeBGCount	0x3191d	void	id	sel
METHOD	Octopus	+	resetChangeBGCount	0x31911	void	id	sel
METHOD	Octopus	+	checkPattern:	0x32199	u1	id	sel	i4
METHOD	Octopus	+	setPattern:	0x321c1	void	id	sel	i4
METHOD	Octopus	+	resetPattern	0x318ed	void	id	sel
METHOD	MyEAGLView	-	setContext:	0x33f99	void	id	sel	id
METHOD	MyEAGLView	-	context	0x339a9	id	id	sel
METHOD	MyEAGLView	-	dealloc	0x339b5	void	id	sel
METHOD	MyEAGLView	-	getMovewidth::	0x338f5	u1	id	sel	i4	i4
METHOD	MyEAGLView	-	getTouchMoveDist	0x338a9	f4	id	sel
METHOD	MyEAGLView	-	getOldMovePos:	0x34285	struct(CGPoint)	id	sel	i4
METHOD	MyEAGLView	-	getMovePos:	0x3429d	struct(CGPoint)	id	sel	i4
METHOD	MyEAGLView	-	getTouchPos:	0x342b5	struct(CGPoint)	id	sel	i4
METHOD	MyEAGLView	-	Key_Speac	0x33885	i4	id	sel
METHOD	MyEAGLView	-	getTouchFlag:	0x33875	u1	id	sel	i4
METHOD	MyEAGLView	-	isMultiTouch	0x33869	u1	id	sel
METHOD	MyEAGLView	-	initPich	0x33855	void	id	sel
METHOD	MyEAGLView	-	setPichValue:	0x33819	void	id	sel	f4
METHOD	MyEAGLView	-	getTouchPich	0x33759	f4	id	sel
METHOD	MyEAGLView	-	getTouchFrip::	0x33a21	u1	id	sel	i4	i4
METHOD	MyEAGLView	-	getTouchSlide::	0x33af5	u1	id	sel	i4	i4
METHOD	MyEAGLView	-	getTouchOut:	0x33709	u1	id	sel	i4
METHOD	MyEAGLView	-	getTouchIn:	0x336c5	u1	id	sel	i4
METHOD	MyEAGLView	-	touchesCancelled:withEvent:	0x33b49	void	id	sel	id	id
METHOD	MyEAGLView	-	touchesEnded:withEvent:	0x342cd	void	id	sel	id	id
METHOD	MyEAGLView	-	touchesMoved:withEvent:	0x344f5	void	id	sel	id	id
METHOD	MyEAGLView	-	touchesBegan:withEvent:	0x33fb9	void	id	sel	id	id
METHOD	MyEAGLView	-	initTouchEvent	0x335b1	void	id	sel
METHOD	MyEAGLView	-	clearTouchEvent	0x33581	void	id	sel
METHOD	MyEAGLView	-	destroyFramebuffer	0x33f4d	void	id	sel
METHOD	MyEAGLView	-	createFramebuffer	0x33dbd	i1	id	sel
METHOD	MyEAGLView	-	postRender	0x33d71	void	id	sel
METHOD	MyEAGLView	-	preRender	0x33d35	void	id	sel
METHOD	MyEAGLView	-	initWithFrame:	0x33b5d	id	id	sel	struct(CGRect)
METHOD	MyEAGLView	+	layerClass	0x33d19	id	id	sel
METHOD	Missile	-	set:index:scale:	0x35359	void	id	sel	ptr(struct(EneDat))	i2	f4
METHOD	Missile	-	render	0x3482d	void	id	sel
METHOD	Missile	-	update	0x34d7d	void	id	sel
METHOD	Missile	-	reset	0x34715	void	id	sel
METHOD	Missile	-	initWithParameter:	0x3479d	id	id	sel	ptr(void)
METHOD	WeaponBase	-	type	0x359ed	i4	id	sel
METHOD	WeaponBase	-	render	0x359eb	void	id	sel
METHOD	WeaponBase	-	update	0x359e9	void	id	sel
METHOD	WeaponBase	-	reset	0x359e7	void	id	sel
METHOD	WeaponBase	-	init	0x359e5	id	id	sel
METHOD	FullScreenEffect	+	setWhiteFadeIn:	0x35ae5	void	id	sel	i4
METHOD	FullScreenEffect	+	setWhiteFadeOut:	0x35abd	void	id	sel	i4
METHOD	FullScreenEffect	+	setDestructEffect	0x35ab1	void	id	sel
METHOD	FullScreenEffect	+	setDamageEffect:	0x35a9d	void	id	sel	i4
METHOD	FullScreenEffect	+	cleanCameraDust	0x35a89	void	id	sel
METHOD	FullScreenEffect	+	messCameraDust_wallbreak	0x35a59	void	id	sel
METHOD	FullScreenEffect	+	messCameraDust_walldamage	0x35a29	void	id	sel
METHOD	FullScreenEffect	+	drawWhiteFadeOut	0x360a1	void	id	sel
METHOD	FullScreenEffect	+	drawDestruct	0x36311	void	id	sel
METHOD	FullScreenEffect	+	drawPlayerDamage	0x36135	void	id	sel
METHOD	FullScreenEffect	+	drawRain	0x363d1	void	id	sel
METHOD	FullScreenEffect	+	drawCameraDust	0x361c1	void	id	sel
METHOD	FullScreenEffect	+	proc	0x35b85	void	id	sel
METHOD	FullScreenEffect	+	reset	0x359f9	void	id	sel
METHOD	FullScreenEffect	+	release	0x35b0d	void	id	sel
METHOD	FullScreenEffect	+	init	0x35da5	void	id	sel
METHOD	FallingObjects	+	private_setFallingObject::	0x365b1	void	id	sel	i4	i4
METHOD	FallingObjects	+	draw	0x36dbd	void	id	sel
METHOD	FallingObjects	+	proc	0x367c9	void	id	sel
METHOD	FallingObjects	+	reset	0x36d11	void	id	sel
METHOD	FallingObjects	+	release	0x36515	void	id	sel
METHOD	FallingObjects	+	init	0x36539	void	id	sel
METHOD	GameMsg	+	isAdviceContinuePermitOfStage:BgNum:AdviceNum:	0x372f1	i1	id	sel	i4	i4	i4
METHOD	GameMsg	+	setAdviceContinueBgNum:	0x372a9	void	id	sel	i4
METHOD	GameMsg	+	numAdviceContinueOfStage:	0x374f9	i4	id	sel	i4
METHOD	GameMsg	+	numAdviceOfStage:isSurvival:	0x37415	i4	id	sel	i4	i1
METHOD	GameMsg	+	isAdviceOfExtraSurvival::::	0x372b5	i1	id	sel	i4	i4	i4	i4
METHOD	GameMsg	+	init	0x37271	void	id	sel
METHOD	Camera	+	getPosBaseY	0x3776d	f4	id	sel
METHOD	Camera	+	getPosBaseX	0x37761	f4	id	sel
METHOD	Camera	+	getShakeY	0x37755	f4	id	sel
METHOD	Camera	+	getShakeX	0x37749	f4	id	sel
METHOD	Camera	+	getShakePower	0x3773d	i4	id	sel
METHOD	Camera	+	getDrawAdjY	0x37731	f4	id	sel
METHOD	Camera	+	getDrawAdjX	0x37725	f4	id	sel
METHOD	Camera	+	getDrawScale	0x37719	f4	id	sel
METHOD	Camera	+	getPosY	0x3770d	f4	id	sel
METHOD	Camera	+	getPosX	0x37701	f4	id	sel
METHOD	Camera	+	getDrawPosY_pl:	0x376cd	f4	id	sel	f4
METHOD	Camera	+	getDrawPosX_pl:	0x37699	f4	id	sel	f4
METHOD	Camera	+	getDrawPosY:	0x37779	f4	id	sel	f4
METHOD	Camera	+	getDrawPosX:	0x377d5	f4	id	sel	f4
METHOD	Camera	+	shake:	0x37639	void	id	sel	i4
METHOD	Camera	+	proc	0x3794d	void	id	sel
METHOD	Camera	+	release	0x37831	void	id	sel
METHOD	Camera	+	init	0x37845	void	id	sel
METHOD	Player	+	private_getDamageVal	0x38c75	i4	id	sel
METHOD	Player	+	private_LifeArart	0x38fe9	void	id	sel
METHOD	Player	+	drawREX_Switch	0x3a3a9	void	id	sel
METHOD	Player	+	private_drawREX_M_Sight	0x3a819	void	id	sel
METHOD	Player	+	private_drawREX_B_Sight	0x3ae51	void	id	sel
METHOD	Player	+	private_drawRailgunSight	0x3af65	void	id	sel
METHOD	Player	+	private_drawRpgSight	0x3b699	void	id	sel
METHOD	Player	+	private_drawSvdSight	0x3bb65	void	id	sel
METHOD	Player	+	private_drawM4Sight	0x39271	void	id	sel
METHOD	Player	+	drawSight	0x38ce5	void	id	sel
METHOD	Player	+	private_drawREX	0x3c025	void	id	sel
METHOD	Player	+	private_drawSnake_Boxing	0x3c36d	void	id	sel
METHOD	Player	+	private_drawSnake_Doll	0x3c591	void	id	sel
METHOD	Player	+	private_drawSnake	0x3c93d	void	id	sel
METHOD	Player	+	drawPlayer	0x38d51	void	id	sel
METHOD	Player	+	private_procStealth	0x3a129	void	id	sel
METHOD	Player	+	private_procSightChangeAnim	0x38bcd	void	id	sel
METHOD	Player	+	private_setSightChangeAnim:	0x38ba9	void	id	sel	i4
METHOD	Player	+	private_setSightMode:	0x3a341	void	id	sel	i4
METHOD	Player	+	private_getRotPoint:rot:	0x3d165	struct(CGPoint)	id	sel	struct(CGPoint)	i4
METHOD	Player	+	private_CheckShootHit:	0x3eac9	void	id	sel	struct(CGPoint)
METHOD	Player	+	private_Breath	0x3a275	void	id	sel
METHOD	Player	+	private_Shoot	0x3ec75	void	id	sel
METHOD	Player	+	private_CheckTouchAndChangeWeapon	0x3d1cd	u1	id	sel
METHOD	Player	+	private_CheckPichAndChangeWeapon	0x3902d	void	id	sel
METHOD	Player	+	private_MoveSight	0x38a51	void	id	sel
METHOD	Player	+	private_ControlPlayer	0x394dd	void	id	sel
METHOD	Player	+	private_UpdateController	0x3d225	void	id	sel
METHOD	Player	+	getSightChangeAnimeStat	0x38a45	i4	id	sel
METHOD	Player	+	getStealthAlpha	0x38a39	i4	id	sel
METHOD	Player	+	isStealth	0x38a2d	u1	id	sel
METHOD	Player	+	getDeadCnt	0x38a1d	i4	id	sel
METHOD	Player	+	isDamaged	0x38a09	u1	id	sel
METHOD	Player	+	getSitCnt	0x389f9	i4	id	sel
METHOD	Player	+	isNoDamage	0x389e9	u1	id	sel
METHOD	Player	+	isAvoid_orDucking	0x389cd	u1	id	sel
METHOD	Player	+	isAvoid	0x38d99	u1	id	sel
METHOD	Player	+	getWeapon	0x389c1	i4	id	sel
METHOD	Player	+	finishRise	0x389ad	void	id	sel
METHOD	Player	+	getStatLife	0x389a1	i4	id	sel
METHOD	Player	+	getStat	0x38995	i4	id	sel
METHOD	Player	+	getSightScale	0x38989	f4	id	sel
METHOD	Player	+	getSightPosY	0x3897d	f4	id	sel
METHOD	Player	+	getSightPosX	0x38971	f4	id	sel
METHOD	Player	+	getControlMode	0x38965	i4	id	sel
METHOD	Player	+	setControlMode:	0x38959	void	id	sel	i4
METHOD	Player	+	isDanger	0x38931	u1	id	sel
METHOD	Player	+	getMaxHP	0x38925	i4	id	sel
METHOD	Player	+	getHP	0x38919	i4	id	sel
METHOD	Player	+	setBoxing	0x388e1	void	id	sel
METHOD	Player	+	missDoll	0x388c9	void	id	sel
METHOD	Player	+	setDoll	0x38895	void	id	sel
METHOD	Player	+	setREX	0x38855	void	id	sel
METHOD	Player	+	setRailgun	0x3911d	void	id	sel
METHOD	Player	+	setRPG7	0x3918d	void	id	sel
METHOD	Player	+	setStealth	0x38829	void	id	sel
METHOD	Player	+	setCure:	0x387fd	void	id	sel	i4
METHOD	Player	+	setDamage_FriendFire:	0x391fd	void	id	sel	i4
METHOD	Player	+	setDamage:::	0x3d449	void	id	sel	i4	f4	f4
METHOD	Player	+	setHP:	0x387f1	void	id	sel	i4
METHOD	Player	+	initHP:	0x387e1	void	id	sel	i4
METHOD	Player	+	proc	0x3d6cd	void	id	sel
METHOD	Player	+	release	0x38dd1	void	id	sel
METHOD	Player	+	init	0x3de29	void	id	sel
METHOD	Player	+	resetForStageChange	0x3e8bd	void	id	sel
METHOD	Player	+	setgGlView:	0x387d5	void	id	sel	id
METHOD	Stage	+	isLoadedBG:	0x3f285	u1	id	sel	i4
METHOD	Stage	+	setLoadedBG::	0x3f26d	void	id	sel	i4	u1
METHOD	Stage	+	decLoadChangeCnt	0x3f25d	void	id	sel
METHOD	Stage	+	incLoadChangeCnt	0x3f24d	void	id	sel
METHOD	Stage	+	clearLoadChangeCnt	0x3f241	void	id	sel
METHOD	Stage	+	getLoadChangeCnt	0x3f235	i4	id	sel
METHOD	Stage	+	isLoadChange	0x3f229	u1	id	sel
METHOD	Stage	+	setLoadChange:	0x3f21d	void	id	sel	u1
METHOD	Stage	+	getMaxPtn	0x3f211	i4	id	sel
METHOD	Stage	+	setMaxPtn:	0x3f201	void	id	sel	i4
METHOD	Stage	+	getNowPtn	0x3f1f5	i4	id	sel
METHOD	Stage	+	incNowPtn	0x3f1e5	void	id	sel
METHOD	Stage	+	getEnemyMax	0x3f1d9	i4	id	sel
METHOD	Stage	+	setEnemyMax:	0x3f1c9	void	id	sel	i4
METHOD	Stage	+	getDestNum_Ptn	0x3f1bd	i4	id	sel
METHOD	Stage	+	addDestNum_Ptn:	0x3f1a9	void	id	sel	i4
METHOD	Stage	+	addDestNum:	0x3f195	void	id	sel	i4
METHOD	Stage	+	getRestDestNum	0x3f181	i4	id	sel
METHOD	Stage	+	getClearDestNum	0x3f175	i4	id	sel
METHOD	Stage	+	setClearDestNum:	0x3f165	void	id	sel	i4
METHOD	Stage	+	getClearCheck	0x3f159	i4	id	sel
METHOD	Stage	+	setClearCheck:	0x3f14d	void	id	sel	i4
METHOD	Stage	+	getSubNum	0x3f141	i4	id	sel
METHOD	Stage	+	setSubNum:	0x3f135	void	id	sel	i4
METHOD	Stage	+	getBgNum_Log	0x3f129	i4	id	sel
METHOD	Stage	+	getBgNum	0x3f11d	i4	id	sel
METHOD	Stage	+	setBgNum:	0x3f109	void	id	sel	i4
METHOD	Stage	+	getNum	0x3f0fd	i4	id	sel
METHOD	Stage	+	setNum:	0x3f0ed	void	id	sel	i4
METHOD	Stage	+	getDepthInfo:	0x3f2a1	i4	id	sel	ptr(struct(CGPoint))
METHOD	Stage	+	releaseData	0x3f331	void	id	sel
METHOD	Stage	+	loadData	0x3f3d1	void	id	sel
METHOD	Stage	+	draw	0x3f62d	void	id	sel
METHOD	Stage	+	proc	0x3f0d1	void	id	sel
METHOD	Stage	+	resetGameParams	0x3f0bd	void	id	sel
METHOD	Stage	+	init	0x3f391	void	id	sel
METHOD	MenuScroll	-	isScroll	0x40089	i1	id	sel
METHOD	MenuScroll	-	isMoveOfBlock:	0x4003d	i1	id	sel	f4
METHOD	MenuScroll	-	isMove	0x40019	i1	id	sel
METHOD	MenuScroll	-	scrollPos	0x3fff5	f4	id	sel
METHOD	MenuScroll	-	updateWithTouch:touchPoint:touchMoveOld:touchMoveNow:	0x3f969	void	id	sel	i1	struct(CGPoint)	struct(CGPoint)	struct(CGPoint)
METHOD	MenuScroll	-	setScrollWithSize:setSizeMin:	0x40101	void	id	sel	struct(CGSize)	i1
METHOD	MenuScroll	-	setScrollWithSize:	0x40095	void	id	sel	struct(CGSize)
METHOD	MenuScroll	-	setOverRangeSize:	0x3f95d	void	id	sel	f4
METHOD	MenuScroll	-	setScrollPos:	0x3f8f9	void	id	sel	f4
METHOD	MenuScroll	-	init	0x400b1	id	id	sel
METHOD	ObjectBase	-	_type	0x403cd	i4	id	sel
METHOD	ObjectBase	-	z	0x403c1	ptr(f4)	id	sel
METHOD	ObjectBase	-	getZ	0x403a7	f4	id	sel
METHOD	ObjectBase	-	checkCollision:withRect:	0x402e9	u1	id	sel	ptr(struct(CGRect))	ptr(struct(CGRect))
METHOD	ObjectBase	-	checkCollision:withPoint:	0x40245	u1	id	sel	ptr(struct(CGRect))	ptr(struct(CGPoint))
METHOD	ObjectBase	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x40241	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	ObjectBase	-	checkCollisionWithBullet:hit:distance:	0x4023d	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	ObjectBase	-	getDistance	0x40237	i4	id	sel
METHOD	ObjectBase	-	render	0x40235	void	id	sel
METHOD	Item	-	remove	0x403e9	void	id	sel
METHOD	Item	-	get:::	0x40419	void	id	sel	i4	ptr(struct(CGPoint))	f4
METHOD	Item	-	get	0x408f5	void	id	sel
METHOD	Item	-	set::	0x407d1	void	id	sel	i4	i4
METHOD	Item	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x40471	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Item	-	checkCollisionWithBullet:hit:distance:	0x404ed	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	Item	-	getDistance	0x403d9	i4	id	sel
METHOD	Item	-	renderIcon	0x405b1	void	id	sel
METHOD	Item	-	render	0x405d9	void	id	sel
METHOD	Item	-	update	0x4060d	void	id	sel
METHOD	Item	-	reset	0x40749	void	id	sel
METHOD	Item	-	initWithParameter:	0x4079d	id	id	sel	ptr(void)
METHOD	Drum	-	checkCollisionWithExplosion:	0x409ed	i4	id	sel	ptr(struct(CGRect))
METHOD	Drum	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x40ae5	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Drum	-	checkCollisionWithBullet:hit:distance:	0x40b39	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	Drum	-	getDistance	0x409dd	i4	id	sel
METHOD	Drum	-	render	0x40d25	void	id	sel
METHOD	Drum	-	update	0x40c45	void	id	sel
METHOD	Drum	-	initWithParameter::	0x409b5	id	id	sel	ptr(void)	i2
METHOD	BGObject	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x40fe1	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	BGObject	-	checkCollisionWithBullet:hit:distance:	0x411b1	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	BGObject	-	getDistance	0x40fd5	i4	id	sel
METHOD	BGObject	-	render	0x41465	void	id	sel
METHOD	BGObject	-	initWithParameter::	0x41001	id	id	sel	ptr(void)	i2
METHOD	MimicObject	-	setVisible:	0x41651	void	id	sel	u1
METHOD	MimicObject	-	fadeout	0x41631	void	id	sel
METHOD	MimicObject	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x419f1	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	MimicObject	-	render	0x41699	void	id	sel
METHOD	MimicObject	-	reset	0x415e9	void	id	sel
METHOD	MimicObject	-	initWithParameter::	0x4166d	id	id	sel	ptr(void)	i2
METHOD	Raven	-	setStageChangeCheck	0x41d9d	void	id	sel
METHOD	Raven	-	itemSliderBonus	0x4332d	i4	id	sel
METHOD	Raven	-	setOutsideRange	0x433a1	void	id	sel
METHOD	Raven	-	numSlider	0x43451	i4	id	sel
METHOD	Raven	-	isClusterBomb	0x434d1	i1	id	sel
METHOD	Raven	-	isRoom	0x41d71	i1	id	sel
METHOD	Raven	-	isObstacleOfPosX:	0x41cd9	i1	id	sel	f4
METHOD	Raven	-	resetRaven	0x43525	void	id	sel
METHOD	Raven	-	getEnemyScale	0x41e05	f4	id	sel
METHOD	Raven	-	calculateDamageRaven	0x42965	void	id	sel
METHOD	Raven	-	caluclateDamageWithExplosion:	0x41e9d	i4	id	sel	i4
METHOD	Raven	-	calculateDamage:::::	0x43649	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Raven	-	updateMoveEnd	0x41efd	void	id	sel
METHOD	Raven	-	updateSpecialAttack	0x42a81	void	id	sel
METHOD	Raven	-	updateMoveAttack2	0x438c5	void	id	sel
METHOD	Raven	-	updateMoveAttack	0x42f39	void	id	sel
METHOD	Raven	-	initMove	0x41fbd	void	id	sel
METHOD	Raven	-	updateMove	0x42ff1	void	id	sel
METHOD	Raven	-	updateAttack	0x421a9	void	id	sel
METHOD	Raven	-	updateAppearance	0x422fd	void	id	sel
METHOD	Raven	-	activate	0x41e59	u1	id	sel
METHOD	Raven	-	render	0x4232d	void	id	sel
METHOD	Raven	-	updateAnimation	0x42385	void	id	sel
METHOD	Raven	-	update:	0x4242d	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Raven	-	setNextAction	0x42819	void	id	sel
METHOD	Raven	-	reset	0x42591	void	id	sel
METHOD	Raven	-	dealloc	0x425c5	void	id	sel
METHOD	Raven	-	initWithParameter:index:hp:rpgExplosion:	0x42645	id	id	sel	ptr(struct(EneDat))	i2	ptr(i4)	ptr(struct(EneDat_eff_char))
METHOD	EffectObject	-	render	0x43bab	void	id	sel
METHOD	EffectObject	-	update	0x43ba9	void	id	sel
METHOD	EffectObject	-	initWithParameter:	0x43bed	id	id	sel	i2
METHOD	Wall	+	private_drawHitEffect	0x44cfd	void	id	sel
METHOD	Wall	+	private_procHitEffect	0x43ced	void	id	sel
METHOD	Wall	+	private_setHitEffect:::::	0x44141	void	id	sel	f4	f4	f4	f4	i4
METHOD	Wall	+	private_resetPos::	0x43cc5	void	id	sel	i4	i4
METHOD	Wall	+	hit:	0x441b5	void	id	sel	i4
METHOD	Wall	+	setDamage::	0x43d51	void	id	sel	i4	i4
METHOD	Wall	+	getPackLoad	0x43cc1	i4	id	sel
METHOD	Wall	+	getHP_level	0x43c9d	i4	id	sel
METHOD	Wall	+	getHP	0x43c85	i4	id	sel
METHOD	Wall	+	isAlive	0x43c65	u1	id	sel
METHOD	Wall	+	draw	0x44639	void	id	sel
METHOD	Wall	+	proc	0x443f9	void	id	sel
METHOD	Wall	+	reset	0x43d95	void	id	sel
METHOD	Wall	+	change:	0x43eb1	void	id	sel	i4
METHOD	Wall	+	release	0x440e1	void	id	sel
METHOD	Wall	+	init	0x44061	void	id	sel
METHOD	RavenSlider	-	scaleSlider	0x44ffd	f4	id	sel
METHOD	RavenSlider	-	pointSlider	0x45045	struct(CGPoint)	id	sel
METHOD	RavenSlider	-	isBroken	0x44ff1	i1	id	sel
METHOD	RavenSlider	-	isFinish	0x44f95	i1	id	sel
METHOD	RavenSlider	-	set::sliderAnime::	0x45dd1	void	id	sel	ptr(struct(EneDat))	struct(CGPoint)	i4	i4
METHOD	RavenSlider	-	render	0x45b69	void	id	sel
METHOD	RavenSlider	-	calculateDamage::	0x452e9	i4	id	sel	ptr(i1)	i4
METHOD	RavenSlider	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x45095	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	RavenSlider	-	update	0x4547d	void	id	sel
METHOD	RavenSlider	-	initWithNo:	0x44f39	id	id	sel	i4
METHOD	RavenBomb	-	set:index:scale:anmMissile:anmBomb1:anmBomb2:	0x470c5	void	id	sel	ptr(struct(EneDat))	i2	f4	i4	i4	i4
METHOD	RavenBomb	-	render	0x464a1	void	id	sel
METHOD	RavenBomb	-	update	0x46c51	void	id	sel
METHOD	RavenBomb	-	dealloc	0x46359	void	id	sel
METHOD	RavenBomb	-	initWithParameter:	0x463b5	id	id	sel	ptr(void)
METHOD	ClusterBomb	-	isBomb	0x4617d	i1	id	sel
METHOD	ClusterBomb	-	render	0x466e5	void	id	sel
METHOD	ClusterBomb	-	update	0x461e1	void	id	sel
METHOD	ClusterBomb	-	set:anmBomb1:anmBomb2:index:	0x468e9	void	id	sel	ptr(struct(EneDat))	i4	i4	i4
METHOD	ClusterBomb	-	init	0x4619d	id	id	sel
METHOD	Wolf	-	setItem	0x47f51	void	id	sel
METHOD	Wolf	-	isHalfHaven	0x4759d	i1	id	sel
METHOD	Wolf	-	isAliveHaven	0x47629	i1	id	sel
METHOD	Wolf	-	setSummonHaven	0x47671	void	id	sel
METHOD	Wolf	-	setStateRailgun	0x4787d	void	id	sel
METHOD	Wolf	-	setStageChangeActive	0x474c5	void	id	sel
METHOD	Wolf	-	setStageChange	0x4810d	void	id	sel
METHOD	Wolf	-	resetBoss	0x47919	void	id	sel
METHOD	Wolf	-	getEnemyScale	0x474f1	f4	id	sel
METHOD	Wolf	-	calculateDamageWolf:	0x483f1	void	id	sel	i4
METHOD	Wolf	-	caluclateDamageWithExplosion:	0x47ab5	i4	id	sel	i4
METHOD	Wolf	-	calculateDamage:::::	0x4858d	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Wolf	-	updateMoveAttack	0x49049	void	id	sel
METHOD	Wolf	-	updateAttack	0x487fd	void	id	sel
METHOD	Wolf	-	updateMove	0x48be5	void	id	sel
METHOD	Wolf	-	updateAppearance	0x48211	void	id	sel
METHOD	Wolf	-	initAppearance	0x47b19	void	id	sel
METHOD	Wolf	-	activate	0x47535	u1	id	sel
METHOD	Wolf	-	renderGauge	0x47b51	void	id	sel
METHOD	Wolf	-	render	0x47bf1	void	id	sel
METHOD	Wolf	-	updateAnimation	0x47579	void	id	sel
METHOD	Wolf	-	update:	0x47c6d	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Wolf	-	setNextAction	0x47e35	void	id	sel
METHOD	Wolf	-	reset	0x47cf1	void	id	sel
METHOD	Wolf	-	dealloc	0x47d31	void	id	sel
METHOD	Wolf	-	initWithParameter:index:hp:rpgExplosion:	0x47d6d	id	id	sel	ptr(struct(EneDat))	i2	ptr(i4)	ptr(struct(EneDat_eff_char))
METHOD	Ray	-	Se3DSet:	0x4c77d	void	id	sel	i4
METHOD	Ray	-	setAnimation_GunActive	0x49529	void	id	sel
METHOD	Ray	-	setAnimation_Pose	0x49581	void	id	sel
METHOD	Ray	-	drawFall	0x4c031	void	id	sel
METHOD	Ray	-	drawJump	0x4c325	void	id	sel
METHOD	Ray	-	drawAppear	0x4c581	void	id	sel
METHOD	Ray	-	getAppearPointOfAttack:	0x4ba99	i4	id	sel	i4
METHOD	Ray	-	getAppearPointOfAttack	0x495fd	i4	id	sel
METHOD	Ray	-	getAppearPointOfStart:	0x4bb81	i4	id	sel	i4
METHOD	Ray	-	getAppearPointOfStart	0x49615	i4	id	sel
METHOD	Ray	-	isBrokenArms	0x4942b	i1	id	sel
METHOD	Ray	-	getAppearPoint::	0x4bbd1	i4	id	sel	i4	i1
METHOD	Ray	-	getAppearPoint:	0x4bc25	i4	id	sel	i4
METHOD	Ray	-	setWeapon	0x4962d	void	id	sel
METHOD	Ray	-	setStageChangeActive	0x49911	void	id	sel
METHOD	Ray	-	setStageChange	0x4bc95	void	id	sel
METHOD	Ray	-	resetBoss	0x4996d	void	id	sel
METHOD	Ray	-	getEnemyScale	0x49b11	f4	id	sel
METHOD	Ray	-	calculateDamageRay:	0x49c0d	void	id	sel	i4
METHOD	Ray	-	caluclateDamageWithExplosion:	0x49d51	i4	id	sel	i4
METHOD	Ray	-	calculateDamage:::::	0x4bdc9	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Ray	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x49481	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Ray	-	checkCollisionWithBullet:hit:distance:	0x494a9	i4	id	sel	ptr(struct(CGRect))	ptr(i1)	i4
METHOD	Ray	-	updateDie	0x49db5	void	id	sel
METHOD	Ray	-	updateMove	0x4a125	void	id	sel
METHOD	Ray	-	updateSpecialAttack	0x4a55d	void	id	sel
METHOD	Ray	-	updateAttack	0x4aa09	void	id	sel
METHOD	Ray	-	updateAppearance	0x4b139	void	id	sel
METHOD	Ray	-	activate	0x4b585	u1	id	sel
METHOD	Ray	-	renderGauge	0x49429	void	id	sel
METHOD	Ray	-	render	0x4b5f5	void	id	sel
METHOD	Ray	-	updateAnimation	0x494d1	void	id	sel
METHOD	Ray	-	update:	0x494f5	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Ray	-	setNextAction	0x4ba05	void	id	sel
METHOD	Ray	-	reset	0x4b679	void	id	sel
METHOD	Ray	-	dealloc	0x4b6d5	void	id	sel
METHOD	Ray	-	isDemoFlag	0x4941d	i1	id	sel
METHOD	Ray	-	setLockon	0x4940d	void	id	sel
METHOD	Ray	-	isExtraWeaponStart	0x4b731	i1	id	sel
METHOD	Ray	-	initWithParameter:index:hp:	0x4b8b5	id	id	sel	ptr(struct(EneDat))	i2	ptr(i4)
METHOD	Ray	+	setExtraWeapon:	0x49401	void	id	sel	i1
METHOD	Ray	+	isExtraWeapon	0x493f5	i1	id	sel
METHOD	Ray	+	isChangeCharaNeed	0x4b835	i1	id	sel
METHOD	Ray	+	isChangeChara	0x4b869	i1	id	sel
METHOD	Ray	+	getChangeChara	0x493e9	i4	id	sel
METHOD	Ray	+	setChangeCharaComplete	0x4b88d	void	id	sel
METHOD	Ray	+	setChangeChara:	0x493dd	void	id	sel	i4
METHOD	Mantis	-	Se3DSet:	0x4e831	void	id	sel	i4
METHOD	Mantis	-	checkIfDollIsFallen:	0x4cb7d	u1	id	sel	i4
METHOD	Mantis	-	checkIfDollIsFallen	0x4cbc1	u1	id	sel
METHOD	Mantis	-	resurrectDoll:	0x4cbf1	void	id	sel	i4
METHOD	Mantis	-	pickUpDoll:	0x4cc2d	void	id	sel	i4
METHOD	Mantis	-	attackReaver	0x4cc81	void	id	sel
METHOD	Mantis	-	attackReaverWarp	0x4cdc5	void	id	sel
METHOD	Mantis	-	attackReaverInit	0x4ce25	void	id	sel
METHOD	Mantis	-	getKarambitNumber	0x4ce91	i4	id	sel
METHOD	Mantis	-	getWarpInterval	0x4ceb9	i4	id	sel
METHOD	Mantis	-	resetSummon	0x4c8d1	void	id	sel
METHOD	Mantis	-	summonManager	0x4cee1	void	id	sel
METHOD	Mantis	-	setPosAttack	0x4c861	void	id	sel
METHOD	Mantis	-	setPosAppear	0x4e5f5	void	id	sel
METHOD	Mantis	-	setPosHome	0x4cfc9	void	id	sel
METHOD	Mantis	-	initPosition:	0x4c8f5	void	id	sel	i4
METHOD	Mantis	-	setStageChange	0x4c835	void	id	sel
METHOD	Mantis	-	resetBoss	0x4e695	void	id	sel
METHOD	Mantis	-	getEnemyScale	0x4c825	f4	id	sel
METHOD	Mantis	-	caluclateDamageWithExplosion:	0x4c97d	i4	id	sel	i4
METHOD	Mantis	-	calculateDamage:::::	0x4d015	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Mantis	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x4c9a1	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Mantis	-	updateLifeAct	0x4d099	void	id	sel
METHOD	Mantis	-	updateSpecialAttack	0x4d1b1	void	id	sel
METHOD	Mantis	-	updateMove	0x4d7f1	void	id	sel
METHOD	Mantis	-	updateAttack	0x4dc65	void	id	sel
METHOD	Mantis	-	updateAppearance	0x4e0cd	void	id	sel
METHOD	Mantis	-	activate	0x4e575	u1	id	sel
METHOD	Mantis	-	render	0x4ca09	void	id	sel
METHOD	Mantis	-	updateAnimationFrame	0x4ca45	void	id	sel
METHOD	Mantis	-	updateAnimation	0x4ca81	void	id	sel
METHOD	Mantis	-	update:	0x4caf9	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Mantis	-	setNextAction	0x4e279	void	id	sel
METHOD	Mantis	-	reset	0x4e381	void	id	sel
METHOD	Mantis	-	dealloc	0x4e3b5	void	id	sel
METHOD	Mantis	-	initWithParameter:index:hp:	0x4e435	id	id	sel	ptr(struct(EneDat))	i2	ptr(i4)
METHOD	Liquid	-	getAttackPhase	0x4e901	i4	id	sel
METHOD	Liquid	-	isFlagDemo	0x4e8f5	i1	id	sel
METHOD	Liquid	-	isFlagZoom	0x4e8dd	i1	id	sel
METHOD	Liquid	-	attackStep	0x4e8d1	i4	id	sel
METHOD	Liquid	-	Se3DSet:	0x501e9	void	id	sel	i4
METHOD	Liquid	-	setAttackSE	0x4ea35	void	id	sel
METHOD	Liquid	-	setAttack::	0x4f31d	void	id	sel	i4	i1
METHOD	Liquid	-	isAttackEx	0x4e8b5	i1	id	sel
METHOD	Liquid	-	getDamage:	0x4eaf5	i4	id	sel	i4
METHOD	Liquid	-	isAttack:	0x50291	i1	id	sel	i4
METHOD	Liquid	-	getTypeAttack	0x4f7f5	i4	id	sel
METHOD	Liquid	-	resetBoss	0x4f875	void	id	sel
METHOD	Liquid	-	getEnemyScale	0x4e8ab	f4	id	sel
METHOD	Liquid	-	updateDie	0x50359	void	id	sel
METHOD	Liquid	-	calculateDamage:::::	0x4fa39	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	Liquid	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x4fdad	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Liquid	-	updateMoveEnd	0x4e979	void	id	sel
METHOD	Liquid	-	updateSpecialAttack	0x50065	void	id	sel
METHOD	Liquid	-	updateMoveAttack2	0x4e99d	void	id	sel
METHOD	Liquid	-	updateMoveAttack	0x4eb6d	void	id	sel
METHOD	Liquid	-	updateMove	0x4ec19	void	id	sel
METHOD	Liquid	-	updateAttack	0x4ecf1	void	id	sel
METHOD	Liquid	-	updateAppearance	0x4f0a1	void	id	sel
METHOD	Liquid	-	activate	0x4e8a7	u1	id	sel
METHOD	Liquid	-	renderGauge	0x4e8a5	void	id	sel
METHOD	Liquid	-	render	0x4f1bd	void	id	sel
METHOD	Liquid	-	updateAnimation	0x4f241	void	id	sel
METHOD	Liquid	-	update:	0x4e9c1	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	Liquid	-	setNextAction	0x4ff89	void	id	sel
METHOD	Liquid	-	reset	0x4f2a5	void	id	sel
METHOD	Liquid	-	dealloc	0x4ea11	void	id	sel
METHOD	Liquid	-	initWithParameter:index:hp:	0x4f2d9	id	id	sel	ptr(struct(EneDat))	i2	ptr(i4)
METHOD	HavenSoldierA	-	calculateDamage:::::	0x517c1	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	HavenSoldierA	-	changeAnimation	0x51829	u1	id	sel
METHOD	HavenSoldierA	-	updateMovePostProcess	0x51679	void	id	sel
METHOD	HavenSoldierA	-	updateMoveProcess	0x518ad	void	id	sel
METHOD	HavenSoldierA	-	updateAttackPostProcess	0x516ad	void	id	sel
METHOD	HavenSoldierA	-	updateAttackProcess	0x51909	void	id	sel
METHOD	HavenSoldierA	-	updateAttackPreProcess	0x51959	void	id	sel
METHOD	HavenSoldierA	-	initAppearance	0x519ad	void	id	sel
METHOD	HavenSoldierA	-	disappear	0x5174d	void	id	sel
METHOD	HavenSoldierB	-	getMovePoint	0x52081	i4	id	sel
METHOD	HavenSoldierB	-	resetHavenSoldier	0x51ba1	void	id	sel
METHOD	HavenSoldierB	-	changeAnimation	0x51e35	u1	id	sel
METHOD	HavenSoldierB	-	updateDie	0x51bcd	void	id	sel
METHOD	HavenSoldierB	-	updateMovePostProcess	0x51c55	void	id	sel
METHOD	HavenSoldierB	-	updateMoveProcess	0x51b31	void	id	sel
METHOD	HavenSoldierB	-	updateMovePreProcess	0x51cbd	void	id	sel
METHOD	HavenSoldierB	-	updateAttackPostProcess	0x5217d	void	id	sel
METHOD	HavenSoldierB	-	initAppearance	0x51f11	void	id	sel
METHOD	HavenSoldierB	-	appearPoint	0x51b25	i4	id	sel
METHOD	HavenSoldierB	-	activate	0x51d45	u1	id	sel
METHOD	HavenSoldierB	-	reset	0x51da1	void	id	sel
METHOD	HavenSoldierB	-	initWithParameter:index:	0x51dd5	id	id	sel	ptr(struct(EneDat))	i2
METHOD	HavenSoldierB	+	setLastPoint:	0x51b19	void	id	sel	i2
METHOD	HavenSoldierB	+	getLastPoint	0x51b09	i2	id	sel
METHOD	HavenSoldierB	+	clearMovablePoint:	0x51af1	void	id	sel	i4
METHOD	HavenSoldierB	+	setMovablePoint:	0x51ad9	void	id	sel	i4
METHOD	HavenSoldierB	+	initMovablePoints	0x51ac1	void	id	sel
METHOD	HavenSoldierB	+	getMovablePoints	0x51ab1	u8	id	sel
METHOD	HavenSoldierB	+	decCount	0x51a9d	void	id	sel
METHOD	HavenSoldierB	+	incCount	0x51a8d	void	id	sel
METHOD	HavenSoldierB	+	setCount:	0x51a81	void	id	sel	i2
METHOD	HavenSoldierB	+	getCount	0x51a75	i2	id	sel
METHOD	PlayerMissile	+	cancelREX_M	0x52217	void	id	sel
METHOD	PlayerMissile	+	startREX_M:::	0x52b65	void	id	sel	ptr(struct(CGPoint))	ptr(struct(CGPoint))	i4
METHOD	PlayerMissile	+	startRPG::	0x52241	void	id	sel	ptr(struct(CGPoint))	ptr(struct(CGPoint))
METHOD	PlayerMissile	+	draw	0x52215	void	id	sel
METHOD	PlayerMissile	+	proc	0x52491	void	id	sel
METHOD	PlayerMissile	+	init	0x521f9	void	id	sel
METHOD	DebugDisp	+	setDebugExpRect::	0x52eb1	void	id	sel	ptr(struct(CGRect))	i4
METHOD	DebugDisp	+	setDebugRect:::	0x52e65	void	id	sel	i4	ptr(struct(CGRect))	i4
METHOD	DebugDisp	+	draw	0x52ef5	void	id	sel
METHOD	DebugDisp	+	proc	0x52e21	void	id	sel
METHOD	DebugDisp	+	release	0x52ded	void	id	sel
METHOD	DebugDisp	+	init	0x52db9	void	id	sel
METHOD	DwarfGekko	-	setMoveAnimation	0x533d9	void	id	sel
METHOD	DwarfGekko	-	resetDwarfGekko	0x53421	void	id	sel
METHOD	DwarfGekko	-	deadSound:	0x538f5	void	id	sel	u1
METHOD	DwarfGekko	-	calculateDamage:::::	0x5393d	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	DwarfGekko	-	changeAnimation	0x53a31	u1	id	sel
METHOD	DwarfGekko	-	attackSound	0x53ad9	void	id	sel
METHOD	DwarfGekko	-	attack	0x53459	void	id	sel
METHOD	DwarfGekko	-	updateDie	0x53c3d	void	id	sel
METHOD	DwarfGekko	-	initMove	0x53485	void	id	sel
METHOD	DwarfGekko	-	updateAttackPostProcess	0x532cd	void	id	sel
METHOD	DwarfGekko	-	updateAttackProsess	0x53349	void	id	sel
METHOD	DwarfGekko	-	updateAppearancePostProcess	0x53b19	void	id	sel
METHOD	DwarfGekko	-	updateAppearanceProcess	0x5338d	void	id	sel
METHOD	DwarfGekko	-	initAppearance	0x53b79	void	id	sel
METHOD	DwarfGekko	-	isTheLastMember:	0x534c5	u1	id	sel	ptr(u8)
METHOD	DwarfGekko	-	isLeader	0x532c1	u1	id	sel
METHOD	DwarfGekko	-	groupMemberCount	0x532b5	i4	id	sel
METHOD	DwarfGekko	-	groupIsActivatable	0x5354d	u1	id	sel
METHOD	DwarfGekko	-	groupAppearPoints	0x532a5	u8	id	sel
METHOD	DwarfGekko	-	groupIsAnnihilated	0x53599	u1	id	sel
METHOD	DwarfGekko	-	addGroupMenber:	0x53609	void	id	sel	id
METHOD	DwarfGekko	-	activate	0x536b1	u1	id	sel
METHOD	DwarfGekko	-	reset	0x53779	void	id	sel
METHOD	DwarfGekko	-	initWithParameter:index:	0x537ad	id	id	sel	ptr(struct(EneDat))	i2
METHOD	DwarfGekko	+	decCount	0x53291	void	id	sel
METHOD	DwarfGekko	+	incCount	0x53281	void	id	sel
METHOD	DwarfGekko	+	resetCount	0x538bd	void	id	sel
METHOD	DwarfGekko	+	getCount	0x53275	i2	id	sel
METHOD	DwarfGekko	+	getCountMax	0x53269	i2	id	sel
METHOD	DwarfGekko	+	resetTurnSE	0x5325d	void	id	sel
METHOD	DwarfGekko	+	nextTurnSE	0x53e85	i4	id	sel
METHOD	SelfDestructionGekko	-	getMovePoint	0x54435	i4	id	sel
METHOD	SelfDestructionGekko	-	renderPlasma	0x548ed	void	id	sel
METHOD	SelfDestructionGekko	-	renderLight	0x54b1d	void	id	sel
METHOD	SelfDestructionGekko	-	updateEffect	0x53f59	void	id	sel
METHOD	SelfDestructionGekko	-	resetEffect	0x5403d	void	id	sel
METHOD	SelfDestructionGekko	-	resetSelfDestructionGekko	0x540a5	void	id	sel
METHOD	SelfDestructionGekko	-	changeAnimation	0x54d95	u1	id	sel
METHOD	SelfDestructionGekko	-	updateDie	0x54531	void	id	sel
METHOD	SelfDestructionGekko	-	updateSelfDestruction	0x54609	void	id	sel
METHOD	SelfDestructionGekko	-	initSelfDestruction	0x53f57	void	id	sel
METHOD	SelfDestructionGekko	-	updateAttackProcess	0x53f55	void	id	sel
METHOD	SelfDestructionGekko	-	updateAttack	0x547f1	void	id	sel
METHOD	SelfDestructionGekko	-	updateAppearancePostProcess	0x54105	void	id	sel
METHOD	SelfDestructionGekko	-	initAppearance	0x5413d	void	id	sel
METHOD	SelfDestructionGekko	-	calculateDamage:::::	0x546ed	i4	id	sel	ptr(struct(EnemyBase_pStatus))	ptr(i1)	ptr(struct(CGRect))	i4	i4
METHOD	SelfDestructionGekko	-	takeover:	0x54201	void	id	sel	id
METHOD	SelfDestructionGekko	-	appearPoint	0x53f49	i4	id	sel
METHOD	SelfDestructionGekko	-	activate	0x54249	u1	id	sel
METHOD	SelfDestructionGekko	-	render	0x54291	void	id	sel
METHOD	SelfDestructionGekko	-	update:	0x5430d	void	id	sel	ptr(struct(EnemyBase_pStatus))
METHOD	SelfDestructionGekko	-	reset	0x54361	void	id	sel
METHOD	SelfDestructionGekko	-	initWithParameter:index:	0x54395	id	id	sel	ptr(struct(EneDat))	i2
METHOD	SelfDestructionGekko	+	clearCountDown:	0x543f1	void	id	sel	i4
METHOD	SelfDestructionGekko	+	setCountDown::	0x54411	void	id	sel	i4	i4
METHOD	SelfDestructionGekko	+	updateCountDown	0x54f55	void	id	sel
METHOD	SelfDestructionGekko	+	resetCountDown	0x53f21	void	id	sel
METHOD	SelfDestructionGekko	+	getMovablePoints	0x53f15	u4	id	sel
METHOD	SelfDestructionGekko	+	clearMovablePoint:	0x53f01	void	id	sel	i4
METHOD	SelfDestructionGekko	+	setMovablePoint:	0x53eed	void	id	sel	i4
METHOD	SelfDestructionGekko	+	resetMovablePoints	0x53ee1	void	id	sel
METHOD	SelfDestructionGekko	+	getUsedPoints	0x53ed5	u4	id	sel
METHOD	SelfDestructionGekko	+	setUsedPoint:	0x53ec1	void	id	sel	i4
METHOD	SelfDestructionGekko	+	resetUsedPoints	0x53eb5	void	id	sel
METHOD	Railgun	-	isEnd	0x550d5	i1	id	sel
METHOD	Railgun	-	isShot	0x550c9	i1	id	sel
METHOD	Railgun	-	cancel	0x550a1	void	id	sel
METHOD	Railgun	-	shot	0x55085	void	id	sel
METHOD	Railgun	-	render	0x55111	void	id	sel
METHOD	Railgun	-	update	0x55921	void	id	sel
METHOD	Railgun	-	set:scale:anmCharge:anmAtk:anmRay:	0x55555	void	id	sel	ptr(struct(EneDat))	f4	i2	i2	i2
METHOD	Railgun	-	initWithParameter::	0x54fc5	id	id	sel	ptr(void)	i2
METHOD	RayMissile	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x56115	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	RayMissile	-	render	0x56381	void	id	sel
METHOD	RayMissile	-	update	0x5698d	void	id	sel
METHOD	RayMissile	-	isEnd	0x55c69	i1	id	sel
METHOD	RayMissile	-	isBomb	0x55c5d	i1	id	sel
METHOD	RayMissile	-	isShot	0x55c51	i1	id	sel
METHOD	RayMissile	-	set:::	0x55c75	void	id	sel	ptr(struct(EneDat))	i4	i4
METHOD	RayMissile	-	init	0x55b75	id	id	sel
METHOD	Doll	-	updateAnimation	0x57151	void	id	sel
METHOD	Doll	-	setAnimation:	0x5712d	void	id	sel	i4
METHOD	Doll	-	getGroundPos:	0x57211	void	id	sel	ptr(struct(CGPoint))
METHOD	Doll	-	willFall	0x57571	void	id	sel
METHOD	Doll	-	updateNodes	0x58161	void	id	sel
METHOD	Doll	-	getRootNode	0x572a9	void	id	sel
METHOD	Doll	-	warpOut	0x58085	void	id	sel
METHOD	Doll	-	warpIn	0x57451	void	id	sel
METHOD	Doll	-	resurrect	0x575ed	void	id	sel
METHOD	Doll	-	pickUp	0x57499	void	id	sel
METHOD	Doll	-	getHP	0x57121	i4	id	sel
METHOD	Doll	-	isHit	0x57109	u1	id	sel
METHOD	Doll	-	isStolen	0x570f1	u1	id	sel
METHOD	Doll	-	isDropped	0x570d9	u1	id	sel
METHOD	Doll	-	isActive	0x570c1	u1	id	sel
METHOD	Doll	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x57cad	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Doll	-	render	0x579b1	void	id	sel
METHOD	Doll	-	update	0x5765d	void	id	sel
METHOD	Doll	-	reset	0x57031	void	id	sel
METHOD	Doll	-	initWithParameter:::	0x574d9	id	id	sel	i4	ptr(struct(EneDat))	i4
METHOD	Karambit	-	didHitPlayer	0x5830d	u1	id	sel
METHOD	Karambit	-	status	0x58301	i4	id	sel
METHOD	Karambit	-	isActive	0x582f5	u1	id	sel
METHOD	Karambit	-	isVisible	0x582cd	u1	id	sel
METHOD	Karambit	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x58e41	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	Karambit	-	disappear	0x5827d	void	id	sel
METHOD	Karambit	-	set:	0x587c1	void	id	sel	i4
METHOD	Karambit	-	render	0x58b7d	void	id	sel
METHOD	Karambit	-	update	0x583b5	void	id	sel
METHOD	Karambit	-	reset	0x5826d	void	id	sel
METHOD	Karambit	-	initWithParameter:	0x58339	id	id	sel	ptr(void)
METHOD	FBomb	-	getNextPos::::	0x59f0d	void	id	sel	ptr(struct(FBomb_data))	ptr(f4)	ptr(i4)	i4
METHOD	FBomb	-	set:	0x59389	void	id	sel	i4
METHOD	FBomb	-	isVisible	0x592e9	u1	id	sel
METHOD	FBomb	-	checkCollisionWithBullet_Dmg:weaponType:damage:	0x59859	i4	id	sel	ptr(struct(CGRect))	i4	i4
METHOD	FBomb	-	render	0x59b61	void	id	sel
METHOD	FBomb	-	update	0x594bd	void	id	sel
METHOD	FBomb	-	reset	0x592f5	void	id	sel
METHOD	FBomb	-	initWithParameter:	0x5931d	id	id	sel	ptr(void)
METHOD	FBomb	+	getAliveCountPair:	0x592b9	i4	id	sel	i4
METHOD	FBomb	+	checkAliveFlagsPair:	0x5929d	u1	id	sel	i4
METHOD	FBomb	+	clearAliveFlagsPair:	0x59285	void	id	sel	i4
METHOD	FBomb	+	getAliveCount	0x59265	i4	id	sel
METHOD	FBomb	+	checkAliveFlags	0x59251	u1	id	sel
METHOD	FBomb	+	clearAliveFlag:	0x5923d	void	id	sel	i4
METHOD	FBomb	+	setAliveFlag:	0x59229	void	id	sel	i4
METHOD	FBomb	+	resetAliveFlags	0x5921d	void	id	sel
METHOD	RayWeapon	-	end	0x5a121	void	id	sel
METHOD	RayWeapon	-	isActive	0x5a115	i1	id	sel
METHOD	RayWeapon	-	render	0x5a159	void	id	sel
METHOD	RayWeapon	-	update	0x5a0e9	void	id	sel
METHOD	RayWeapon	-	set:::	0x5a139	void	id	sel	ptr(struct(EneDat))	i4	f4
METHOD	RayWeapon	-	set::::	0x5a095	void	id	sel	ptr(struct(EneDat))	i4	f4	i1
METHOD	RayWeapon	-	init	0x5a005	id	id	sel
METHOD	Texture2D	-	initWithCircle:a:r:g:b:	0x359d	id	id	sel	struct(CGSize)	f4	f4	f4	f4
METHOD	Texture2D	-	initWithRect:a:r:g:b:	0x36bd	id	id	sel	struct(CGSize)	f4	f4	f4	f4
METHOD	Texture2D	-	getImgH	0x2799	f4	id	sel
METHOD	Texture2D	-	getImgW	0x2755	f4	id	sel
METHOD	Texture2D	-	drawInRectRot:ST:	0x2cdd	void	id	sel	struct(CGRect)	struct(CGRect)
METHOD	Texture2D	-	drawInRect:ST:	0x2dfd	void	id	sel	ptr(struct(CGRect))	ptr(struct(CGRect))
METHOD	Texture2D	-	drawInRect:Clip:Anchor:Rot_X:Rot_Y:Rot_Z:	0x2f0d	void	id	sel	struct(CGRect)	struct(CGRect)	i4	f4	f4	f4
METHOD	Texture2D	-	drawInRect:Clip:Rot:Scale:Anchor:	0x3371	void	id	sel	struct(CGRect)	struct(CGRect)	f4	f4	i4
METHOD	Texture2D	-	drawAtPoint:Clip:Rot:Scale:Anchor:	0x33fd	void	id	sel	struct(CGPoint)	struct(CGRect)	f4	f4	i4
METHOD	Texture2D	-	drawAtPoint:	0x34b9	void	id	sel	struct(CGPoint)
METHOD	Texture2D	-	initWithString:dimensions:alignment:fontName:fontSize:a:r:g:b:lineSpace:	0x3df9	id	id	sel	id	struct(CGSize)	i4	id	f4	f4	f4	f4	f4	f4
METHOD	Texture2D	-	initWithString:dimensions:alignment:fontName:fontSize:a:r:g:b:	0x27dd	id	id	sel	id	struct(CGSize)	i4	id	f4	f4	f4	f4	f4
METHOD	Texture2D	-	initWithString:dimensions:alignment:fontName:fontSize:	0x4089	id	id	sel	id	struct(CGSize)	i4	id	f4
METHOD	Texture2D	-	initWithImageA8:	0x37dd	id	id	sel	id
METHOD	Texture2D	-	initWithImage:	0x3ad5	id	id	sel	id
METHOD	Texture2D	-	initWithImageA8Filename:ofType:	0x2829	id	id	sel	id	id
METHOD	Texture2D	-	initWithImageFilename:ofType:	0x28fd	id	id	sel	id	id
