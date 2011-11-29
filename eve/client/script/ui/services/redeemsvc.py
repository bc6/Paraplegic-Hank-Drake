import service
import form
import uix
import listentry
import util
import uicls
import uiconst
import localization
import log

class RedeemService(service.Service):
    __guid__ = 'svc.redeem'

    def __init__(self):
        service.Service.__init__(self)
        self.tokens = None



    def Run(self, *args):
        service.Service.Run(self, *args)



    def GetRedeemTokens(self, force = False):
        if self.tokens is None or force:
            self.tokens = sm.RemoteSvc('userSvc').GetRedeemTokens()
        return self.tokens



    def ReverseRedeem(self, item):
        if eve.Message('ConfirmReverseRedeem', {'type': (TYPEID, item.typeID),
         'quantity': item.stacksize}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        try:
            sm.RemoteSvc('userSvc').ReverseRedeem(item.itemID)

        finally:
            self.tokens = None




    def OpenRedeemWindow(self, charID, stationID):
        if not self.GetRedeemTokens():
            raise UserError('RedeemNoTokens')
        wnd = form.RedeemWindow.GetIfOpen()
        if wnd is None:
            wnd = form.RedeemWindow.Open(charID=charID, stationID=stationID, useDefaultPos=True)
            wnd.left -= 160
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def CloseRedeemWindow(self):
        form.RedeemWindow.CloseIfOpen()



    def ClaimRedeemTokens(self, tokens, charID):
        try:
            sm.RemoteSvc('userSvc').ClaimRedeemTokens(tokens, charID)
        except (UserError,) as e:
            eve.Message(e.msg, e.dict)
        except (Exception,) as e:
            raise 
        self.tokens = None




class RedeemWindow(uicls.Window):
    __guid__ = 'form.RedeemWindow'
    default_windowID = 'redeem'

    def ApplyAttributes--- This code section failed: ---
0	LOAD_GLOBAL       'uicls'
3	LOAD_ATTR         'Window'
6	LOAD_ATTR         'ApplyAttributes'
9	LOAD_FAST         'self'
12	LOAD_FAST         'attributes'
15	CALL_FUNCTION_2   ''
18	POP_TOP           ''
19	LOAD_FAST         'attributes'
22	LOAD_ATTR         'charID'
25	STORE_FAST        'charID'
28	LOAD_FAST         'attributes'
31	LOAD_ATTR         'stationID'
34	STORE_FAST        'stationID'
37	LOAD_CONST        ''
40	LOAD_FAST         'self'
43	STORE_ATTR        'tokens'
46	BUILD_MAP         ''
49	LOAD_FAST         'self'
52	STORE_ATTR        'selectedTokens'
55	LOAD_GLOBAL       'sm'
58	LOAD_ATTR         'StartService'
61	LOAD_CONST        'redeem'
64	CALL_FUNCTION_1   ''
67	LOAD_ATTR         'GetRedeemTokens'
70	CALL_FUNCTION_0   ''
73	LOAD_FAST         'self'
76	STORE_ATTR        'tokens'
79	LOAD_FAST         'self'
82	LOAD_ATTR         'SetWndIcon'
85	LOAD_CONST        'ui_76_64_3'
88	LOAD_CONST        'mainTop'
91	LOAD_CONST        -10
94	CALL_FUNCTION_257 ''
97	POP_TOP           ''
98	LOAD_FAST         'self'
101	LOAD_ATTR         'SetCaption'
104	LOAD_GLOBAL       'localization'
107	LOAD_ATTR         'GetByLabel'
110	LOAD_CONST        'UI/RedeemWindow/RedeemItem'
113	CALL_FUNCTION_1   ''
116	CALL_FUNCTION_1   ''
119	POP_TOP           ''
120	LOAD_FAST         'self'
123	LOAD_ATTR         'SetMinSize'
126	LOAD_CONST        700
129	LOAD_CONST        260
132	BUILD_LIST_2      ''
135	CALL_FUNCTION_1   ''
138	POP_TOP           ''
139	LOAD_FAST         'self'
142	LOAD_ATTR         'NoSeeThrough'
145	CALL_FUNCTION_0   ''
148	POP_TOP           ''
149	LOAD_FAST         'self'
152	LOAD_ATTR         'SetScope'
155	LOAD_CONST        'all'
158	CALL_FUNCTION_1   ''
161	POP_TOP           ''
162	LOAD_FAST         'charID'
165	LOAD_FAST         'self'
168	STORE_ATTR        'charID'
171	LOAD_FAST         'stationID'
174	LOAD_FAST         'self'
177	STORE_ATTR        'stationID'
180	LOAD_FAST         'self'
183	LOAD_ATTR         'sr'
186	LOAD_ATTR         'topParent'
189	LOAD_ATTR         'height'
192	LOAD_CONST        2
195	BINARY_SUBTRACT   ''
196	STORE_FAST        'h'
199	LOAD_GLOBAL       'uicls'
202	LOAD_ATTR         'Container'
205	LOAD_CONST        'name'
208	LOAD_CONST        'picpar'
211	LOAD_CONST        'parent'
214	LOAD_FAST         'self'
217	LOAD_ATTR         'sr'
220	LOAD_ATTR         'topParent'
223	LOAD_CONST        'align'
226	LOAD_GLOBAL       'uiconst'
229	LOAD_ATTR         'TORIGHT'
232	LOAD_CONST        'width'
235	LOAD_FAST         'h'
238	LOAD_CONST        'height'
241	LOAD_FAST         'h'
244	LOAD_CONST        'left'
247	LOAD_GLOBAL       'const'
250	LOAD_ATTR         'defaultPadding'
253	LOAD_CONST        'top'
256	LOAD_GLOBAL       'const'
259	LOAD_ATTR         'defaultPadding'
262	CALL_FUNCTION_1792 ''
265	LOAD_FAST         'self'
268	LOAD_ATTR         'sr'
271	STORE_ATTR        'picParent'
274	LOAD_GLOBAL       'uicls'
277	LOAD_ATTR         'Sprite'
280	LOAD_CONST        'parent'
283	LOAD_FAST         'self'
286	LOAD_ATTR         'sr'
289	LOAD_ATTR         'picParent'
292	LOAD_CONST        'align'
295	LOAD_GLOBAL       'uiconst'
298	LOAD_ATTR         'RELATIVE'
301	LOAD_CONST        'left'
304	LOAD_CONST        1
307	LOAD_CONST        'top'
310	LOAD_CONST        3
313	LOAD_CONST        'height'
316	LOAD_FAST         'h'
319	LOAD_CONST        'width'
322	LOAD_FAST         'h'
325	CALL_FUNCTION_1536 ''
328	LOAD_FAST         'self'
331	LOAD_ATTR         'sr'
334	STORE_ATTR        'pic'
337	LOAD_GLOBAL       'sm'
340	LOAD_ATTR         'GetService'
343	LOAD_CONST        'photo'
346	CALL_FUNCTION_1   ''
349	LOAD_ATTR         'GetPortrait'
352	LOAD_FAST         'charID'
355	LOAD_CONST        64
358	LOAD_FAST         'self'
361	LOAD_ATTR         'sr'
364	LOAD_ATTR         'pic'
367	CALL_FUNCTION_3   ''
370	POP_TOP           ''
371	LOAD_GLOBAL       'uiconst'
374	LOAD_ATTR         'UI_NORMAL'
377	LOAD_FAST         'self'
380	STORE_ATTR        'state'
383	LOAD_GLOBAL       'uicls'
386	LOAD_ATTR         'CaptionLabel'
389	LOAD_CONST        'text'
392	LOAD_GLOBAL       'localization'
395	LOAD_ATTR         'GetByLabel'
398	LOAD_CONST        'UI/RedeemWindow/RedeemItem'
401	CALL_FUNCTION_1   ''
404	LOAD_CONST        'parent'
407	LOAD_FAST         'self'
410	LOAD_ATTR         'sr'
413	LOAD_ATTR         'topParent'
416	LOAD_CONST        'align'
419	LOAD_GLOBAL       'uiconst'
422	LOAD_ATTR         'RELATIVE'
425	LOAD_CONST        'left'
428	LOAD_CONST        60
431	LOAD_CONST        'top'
434	LOAD_CONST        18
437	LOAD_CONST        'state'
440	LOAD_GLOBAL       'uiconst'
443	LOAD_ATTR         'UI_DISABLED'
446	LOAD_CONST        'fontsize'
449	LOAD_CONST        18
452	CALL_FUNCTION_1792 ''
455	LOAD_FAST         'self'
458	LOAD_ATTR         'sr'
461	STORE_ATTR        'windowCaption'
464	LOAD_GLOBAL       'localization'
467	LOAD_ATTR         'GetByLabel'
470	LOAD_CONST        'UI/RedeemWindow/ReedemNumItems'
473	LOAD_CONST        'num'
476	LOAD_GLOBAL       'len'
479	LOAD_FAST         'self'
482	LOAD_ATTR         'tokens'
485	CALL_FUNCTION_1   ''
488	LOAD_CONST        'player'
491	LOAD_FAST         'charID'
494	CALL_FUNCTION_513 ''
497	STORE_FAST        'text'
500	LOAD_CONST        5
503	STORE_FAST        'tp'
506	LOAD_GLOBAL       'uicls'
509	LOAD_ATTR         'EveLabelMedium'
512	LOAD_CONST        'text'
515	LOAD_FAST         'text'
518	LOAD_CONST        'parent'
521	LOAD_FAST         'self'
524	LOAD_ATTR         'sr'
527	LOAD_ATTR         'topParent'
530	LOAD_CONST        'top'
533	LOAD_FAST         'tp'
536	LOAD_CONST        'left'
539	LOAD_CONST        60
542	LOAD_CONST        'state'
545	LOAD_GLOBAL       'uiconst'
548	LOAD_ATTR         'UI_DISABLED'
551	LOAD_CONST        'align'
554	LOAD_GLOBAL       'uiconst'
557	LOAD_ATTR         'TOPRIGHT'
560	CALL_FUNCTION_1536 ''
563	STORE_FAST        't'
566	LOAD_FAST         'tp'
569	LOAD_FAST         't'
572	LOAD_ATTR         'textheight'
575	INPLACE_ADD       ''
576	STORE_FAST        'tp'
579	LOAD_FAST         'stationID'
582	POP_JUMP_IF_FALSE '710'
585	LOAD_GLOBAL       'localization'
588	LOAD_ATTR         'GetByLabel'
591	LOAD_CONST        'UI/RedeemWindow/ItemsDeliveryLocation'
594	LOAD_CONST        'shortStationName'
597	LOAD_GLOBAL       'cfg'
600	LOAD_ATTR         'evelocations'
603	LOAD_ATTR         'Get'
606	LOAD_FAST         'stationID'
609	CALL_FUNCTION_1   ''
612	LOAD_ATTR         'name'
615	LOAD_ATTR         'split'
618	LOAD_CONST        ' - '
621	CALL_FUNCTION_1   ''
624	LOAD_CONST        ''
627	BINARY_SUBSCR     ''
628	CALL_FUNCTION_257 ''
631	STORE_FAST        'text'
634	LOAD_GLOBAL       'uicls'
637	LOAD_ATTR         'EveLabelMedium'
640	LOAD_CONST        'text'
643	LOAD_FAST         'text'
646	LOAD_CONST        'parent'
649	LOAD_FAST         'self'
652	LOAD_ATTR         'sr'
655	LOAD_ATTR         'topParent'
658	LOAD_CONST        'top'
661	LOAD_FAST         'tp'
664	LOAD_CONST        'left'
667	LOAD_CONST        60
670	LOAD_CONST        'state'
673	LOAD_GLOBAL       'uiconst'
676	LOAD_ATTR         'UI_DISABLED'
679	LOAD_CONST        'align'
682	LOAD_GLOBAL       'uiconst'
685	LOAD_ATTR         'TOPRIGHT'
688	CALL_FUNCTION_1536 ''
691	STORE_FAST        't'
694	LOAD_FAST         'tp'
697	LOAD_FAST         't'
700	LOAD_ATTR         'height'
703	INPLACE_ADD       ''
704	STORE_FAST        'tp'
707	JUMP_FORWARD      '785'
710	LOAD_GLOBAL       'localization'
713	LOAD_ATTR         'GetByLabel'
716	LOAD_CONST        'UI/RedeemWindow/IncorrectPlayerLocation'
719	CALL_FUNCTION_1   ''
722	STORE_FAST        'text'
725	LOAD_GLOBAL       'uicls'
728	LOAD_ATTR         'EveLabelMedium'
731	LOAD_CONST        'text'
734	LOAD_FAST         'text'
737	LOAD_CONST        'parent'
740	LOAD_FAST         'self'
743	LOAD_ATTR         'sr'
746	LOAD_ATTR         'topParent'
749	LOAD_CONST        'top'
752	LOAD_FAST         'tp'
755	LOAD_CONST        'left'
758	LOAD_CONST        60
761	LOAD_CONST        'state'
764	LOAD_GLOBAL       'uiconst'
767	LOAD_ATTR         'UI_DISABLED'
770	LOAD_CONST        'align'
773	LOAD_GLOBAL       'uiconst'
776	LOAD_ATTR         'TOPRIGHT'
779	CALL_FUNCTION_1536 ''
782	STORE_FAST        't'
785_0	COME_FROM         '707'
785	LOAD_GLOBAL       'uicls'
788	LOAD_ATTR         'Container'
791	LOAD_CONST        'name'
794	LOAD_CONST        'push'
797	LOAD_CONST        'parent'
800	LOAD_FAST         'self'
803	LOAD_ATTR         'sr'
806	LOAD_ATTR         'main'
809	LOAD_CONST        'align'
812	LOAD_GLOBAL       'uiconst'
815	LOAD_ATTR         'TOLEFT'
818	LOAD_CONST        'width'
821	LOAD_GLOBAL       'const'
824	LOAD_ATTR         'defaultPadding'
827	CALL_FUNCTION_1024 ''
830	POP_TOP           ''
831	LOAD_GLOBAL       'uicls'
834	LOAD_ATTR         'Container'
837	LOAD_CONST        'name'
840	LOAD_CONST        'push'
843	LOAD_CONST        'parent'
846	LOAD_FAST         'self'
849	LOAD_ATTR         'sr'
852	LOAD_ATTR         'main'
855	LOAD_CONST        'align'
858	LOAD_GLOBAL       'uiconst'
861	LOAD_ATTR         'TORIGHT'
864	LOAD_CONST        'width'
867	LOAD_GLOBAL       'const'
870	LOAD_ATTR         'defaultPadding'
873	CALL_FUNCTION_1024 ''
876	POP_TOP           ''
877	LOAD_GLOBAL       'localization'
880	LOAD_ATTR         'GetByLabel'
883	LOAD_CONST        'UI/RedeemWindow/RedeemSelectedItems'
886	CALL_FUNCTION_1   ''
889	LOAD_FAST         'self'
892	LOAD_ATTR         'RedeemSelected'
895	LOAD_CONST        ''
898	LOAD_CONST        84
901	BUILD_TUPLE_4     ''
904	BUILD_LIST_1      ''
907	STORE_FAST        'btns'
910	LOAD_GLOBAL       'uicls'
913	LOAD_ATTR         'ButtonGroup'
916	LOAD_CONST        'btns'
919	LOAD_FAST         'btns'
922	LOAD_CONST        'parent'
925	LOAD_FAST         'self'
928	LOAD_ATTR         'sr'
931	LOAD_ATTR         'main'
934	LOAD_CONST        'unisize'
937	LOAD_CONST        1
940	CALL_FUNCTION_768 ''
943	LOAD_FAST         'self'
946	LOAD_ATTR         'sr'
949	STORE_ATTR        'redeemBtn'
952	LOAD_GLOBAL       'uicls'
955	LOAD_ATTR         'Scroll'
958	LOAD_CONST        'parent'
961	LOAD_FAST         'self'
964	LOAD_ATTR         'sr'
967	LOAD_ATTR         'main'
970	LOAD_CONST        'padTop'
973	LOAD_GLOBAL       'const'
976	LOAD_ATTR         'defaultPadding'
979	CALL_FUNCTION_512 ''
982	LOAD_FAST         'self'
985	LOAD_ATTR         'sr'
988	STORE_ATTR        'itemsScroll'
991	LOAD_CONST        ''
994	LOAD_FAST         'self'
997	LOAD_ATTR         'sr'
1000	LOAD_ATTR         'itemsScroll'
1003	STORE_ATTR        'hiliteSorted'
1006	LOAD_GLOBAL       'uicls'
1009	LOAD_ATTR         'Container'
1012	LOAD_CONST        'name'
1015	LOAD_CONST        'push'
1018	LOAD_CONST        'parent'
1021	LOAD_FAST         'self'
1024	LOAD_ATTR         'sr'
1027	LOAD_ATTR         'main'
1030	LOAD_CONST        'align'
1033	LOAD_GLOBAL       'uiconst'
1036	LOAD_ATTR         'TOBOTTOM'
1039	LOAD_CONST        'width'
1042	LOAD_CONST        6
1045	CALL_FUNCTION_1024 ''
1048	POP_TOP           ''
1049	BUILD_LIST_0      ''
1052	STORE_FAST        'scrolllist'
1055	LOAD_CONST        ''
1058	STORE_FAST        'expireUsed'
1061	SETUP_LOOP        '1531'
1064	LOAD_FAST         'self'
1067	LOAD_ATTR         'tokens'
1070	GET_ITER          ''
1071	FOR_ITER          '1530'
1074	STORE_FAST        'token'
1077	LOAD_GLOBAL       'cfg'
1080	LOAD_ATTR         'invtypes'
1083	LOAD_ATTR         'GetIfExists'
1086	LOAD_FAST         'token'
1089	LOAD_ATTR         'typeID'
1092	CALL_FUNCTION_1   ''
1095	STORE_FAST        'ty'
1098	LOAD_FAST         'token'
1101	LOAD_ATTR         'label'
1104	POP_JUMP_IF_FALSE '1134'
1107	LOAD_FAST         'token'
1110	LOAD_ATTR         'description'
1113	JUMP_IF_TRUE_OR_POP '1137'
1116	LOAD_GLOBAL       'localization'
1119	LOAD_ATTR         'GetByLabel'
1122	LOAD_FAST         'token'
1125	LOAD_ATTR         'label'
1128	CALL_FUNCTION_1   ''
1131	JUMP_FORWARD      '1137'
1134	LOAD_CONST        ''
1137_0	COME_FROM         '1113'
1137_1	COME_FROM         '1131'
1137	STORE_FAST        'desc'
1140	LOAD_FAST         'token'
1143	LOAD_ATTR         'quantity'
1146	STORE_FAST        'qty'
1149	LOAD_FAST         'ty'
1152	LOAD_CONST        ''
1155	COMPARE_OP        'is'
1158	POP_JUMP_IF_FALSE '1250'
1161	LOAD_GLOBAL       'localization'
1164	LOAD_ATTR         'GetByLabel'
1167	LOAD_CONST        'UI/RedeemWindow/UnknownType'
1170	CALL_FUNCTION_1   ''
1173	LOAD_CONST        '<t>%d<t>%s'
1176	LOAD_FAST         'qty'
1179	LOAD_FAST         'desc'
1182	BUILD_TUPLE_2     ''
1185	BINARY_MODULO     ''
1186	BINARY_ADD        ''
1187	STORE_FAST        'msg'
1190	LOAD_FAST         'scrolllist'
1193	LOAD_ATTR         'append'
1196	LOAD_GLOBAL       'listentry'
1199	LOAD_ATTR         'Get'
1202	LOAD_CONST        'Generic'
1205	BUILD_MAP         ''
1208	LOAD_FAST         'msg'
1211	LOAD_CONST        'label'
1214	STORE_MAP         ''
1215	CALL_FUNCTION_2   ''
1218	CALL_FUNCTION_1   ''
1221	POP_TOP           ''
1222	LOAD_GLOBAL       'log'
1225	LOAD_ATTR         'LogWarn'
1228	LOAD_CONST        "A Token was found that we don't know about"
1231	LOAD_FAST         'token'
1234	LOAD_ATTR         'typeID'
1237	LOAD_CONST        'ignoring it for now! Coming Soon(tm)'
1240	CALL_FUNCTION_3   ''
1243	POP_TOP           ''
1244	JUMP_BACK         '1071'
1247	JUMP_FORWARD      '1250'
1250_0	COME_FROM         '1247'
1250	LOAD_CONST        ''
1253	LOAD_FAST         'self'
1256	LOAD_ATTR         'selectedTokens'
1259	LOAD_FAST         'token'
1262	LOAD_ATTR         'tokenID'
1265	LOAD_FAST         'token'
1268	LOAD_ATTR         'massTokenID'
1271	BUILD_TUPLE_2     ''
1274	STORE_SUBSCR      ''
1275	LOAD_FAST         'token'
1278	LOAD_ATTR         'expireDateTime'
1281	POP_JUMP_IF_FALSE '1327'
1284	LOAD_CONST        1
1287	STORE_FAST        'expireUsed'
1290	LOAD_CONST        '%s<t>%s'
1293	LOAD_FAST         'desc'
1296	LOAD_GLOBAL       'localization'
1299	LOAD_ATTR         'GetByLabel'
1302	LOAD_CONST        'UI/RedeemWindow/RedeemExpires'
1305	LOAD_CONST        'expires'
1308	LOAD_FAST         'token'
1311	LOAD_ATTR         'expireDateTime'
1314	CALL_FUNCTION_257 ''
1317	BUILD_TUPLE_2     ''
1320	BINARY_MODULO     ''
1321	STORE_FAST        'desc'
1324	JUMP_FORWARD      '1327'
1327_0	COME_FROM         '1324'
1327	LOAD_FAST         'token'
1330	LOAD_ATTR         'stationID'
1333	POP_JUMP_IF_FALSE '1369'
1336	LOAD_GLOBAL       'localization'
1339	LOAD_ATTR         'GetByLabel'
1342	LOAD_CONST        'UI/RedeemWindow/RedeemableTo'
1345	LOAD_CONST        'desc'
1348	LOAD_FAST         'desc'
1351	LOAD_CONST        'station'
1354	LOAD_FAST         'token'
1357	LOAD_ATTR         'stationID'
1360	CALL_FUNCTION_513 ''
1363	STORE_FAST        'desc'
1366	JUMP_FORWARD      '1369'
1369_0	COME_FROM         '1366'
1369	LOAD_CONST        '%s<t>%s<t>%s'
1372	LOAD_FAST         'ty'
1375	LOAD_ATTR         'typeName'
1378	LOAD_FAST         'qty'
1381	LOAD_FAST         'desc'
1384	BUILD_TUPLE_3     ''
1387	BINARY_MODULO     ''
1388	STORE_FAST        'label'
1391	LOAD_FAST         'scrolllist'
1394	LOAD_ATTR         'append'
1397	LOAD_GLOBAL       'listentry'
1400	LOAD_ATTR         'Get'
1403	LOAD_CONST        'RedeemToken'
1406	BUILD_MAP         ''
1409	LOAD_CONST        ''
1412	LOAD_CONST        'itemID'
1415	STORE_MAP         ''
1416	LOAD_FAST         'token'
1419	LOAD_ATTR         'tokenID'
1422	LOAD_CONST        'tokenID'
1425	STORE_MAP         ''
1426	LOAD_FAST         'token'
1429	LOAD_ATTR         'massTokenID'
1432	LOAD_CONST        'massTokenID'
1435	STORE_MAP         ''
1436	LOAD_FAST         'token'
1439	LOAD_CONST        'info'
1442	STORE_MAP         ''
1443	LOAD_FAST         'ty'
1446	LOAD_ATTR         'typeID'
1449	LOAD_CONST        'typeID'
1452	STORE_MAP         ''
1453	LOAD_FAST         'token'
1456	LOAD_ATTR         'stationID'
1459	LOAD_CONST        'stationID'
1462	STORE_MAP         ''
1463	LOAD_FAST         'label'
1466	LOAD_CONST        'label'
1469	STORE_MAP         ''
1470	LOAD_FAST         'qty'
1473	LOAD_CONST        'quantity'
1476	STORE_MAP         ''
1477	LOAD_CONST        1
1480	LOAD_CONST        'getIcon'
1483	STORE_MAP         ''
1484	LOAD_FAST         'token'
1487	LOAD_ATTR         'tokenID'
1490	LOAD_FAST         'token'
1493	LOAD_ATTR         'massTokenID'
1496	BUILD_TUPLE_2     ''
1499	LOAD_CONST        'retval'
1502	STORE_MAP         ''
1503	LOAD_FAST         'self'
1506	LOAD_ATTR         'OnTokenChange'
1509	LOAD_CONST        'OnChange'
1512	STORE_MAP         ''
1513	LOAD_GLOBAL       'True'
1516	LOAD_CONST        'checked'
1519	STORE_MAP         ''
1520	CALL_FUNCTION_2   ''
1523	CALL_FUNCTION_1   ''
1526	POP_TOP           ''
1527	JUMP_BACK         '1071'
1530_0	COME_FROM         '1071'
1530	POP_BLOCK         ''
1531_0	COME_FROM         '1061'
1531	LOAD_FAST         'self'
1534	LOAD_ATTR         'sr'
1537	LOAD_ATTR         'itemsScroll'
1540	LOAD_CONST        ''
1543	COMPARE_OP        'is not'
1546	POP_JUMP_IF_FALSE '1763'
1549	LOAD_CONST        'itemsScroll'
1552	LOAD_FAST         'self'
1555	LOAD_ATTR         'sr'
1558	LOAD_ATTR         'itemsScroll'
1561	LOAD_ATTR         'sr'
1564	STORE_ATTR        'id'
1567	LOAD_CONST        ''
1570	LOAD_FAST         'self'
1573	LOAD_ATTR         'sr'
1576	LOAD_ATTR         'itemsScroll'
1579	LOAD_ATTR         'sr'
1582	STORE_ATTR        'lastSelected'
1585	BUILD_MAP         ''
1588	LOAD_CONST        50
1591	LOAD_GLOBAL       'localization'
1594	LOAD_ATTR         'GetByLabel'
1597	LOAD_CONST        'UI/Common/Type'
1600	CALL_FUNCTION_1   ''
1603	STORE_MAP         ''
1604	LOAD_FAST         'self'
1607	LOAD_ATTR         'sr'
1610	LOAD_ATTR         'itemsScroll'
1613	LOAD_ATTR         'sr'
1616	STORE_ATTR        'minColumnWidth'
1619	LOAD_GLOBAL       'localization'
1622	LOAD_ATTR         'GetByLabel'
1625	LOAD_CONST        'UI/Common/Type'
1628	CALL_FUNCTION_1   ''
1631	LOAD_GLOBAL       'localization'
1634	LOAD_ATTR         'GetByLabel'
1637	LOAD_CONST        'UI/Common/Quantity'
1640	CALL_FUNCTION_1   ''
1643	LOAD_GLOBAL       'localization'
1646	LOAD_ATTR         'GetByLabel'
1649	LOAD_CONST        'UI/Common/Description'
1652	CALL_FUNCTION_1   ''
1655	BUILD_LIST_3      ''
1658	STORE_FAST        'headers'
1661	LOAD_FAST         'expireUsed'
1664	LOAD_CONST        1
1667	COMPARE_OP        '=='
1670	POP_JUMP_IF_FALSE '1732'
1673	LOAD_FAST         'headers'
1676	LOAD_ATTR         'append'
1679	LOAD_GLOBAL       'localization'
1682	LOAD_ATTR         'GetByLabel'
1685	LOAD_CONST        'UI/Common/Expires'
1688	CALL_FUNCTION_1   ''
1691	CALL_FUNCTION_1   ''
1694	POP_TOP           ''
1695	BUILD_MAP         ''
1698	LOAD_CONST        80
1701	LOAD_GLOBAL       'localization'
1704	LOAD_ATTR         'GetByLabel'
1707	LOAD_CONST        'UI/Common/Expires'
1710	CALL_FUNCTION_1   ''
1713	STORE_MAP         ''
1714	LOAD_FAST         'self'
1717	LOAD_ATTR         'sr'
1720	LOAD_ATTR         'itemsScroll'
1723	LOAD_ATTR         'sr'
1726	STORE_ATTR        'fixedColumns'
1729	JUMP_FORWARD      '1732'
1732_0	COME_FROM         '1729'
1732	LOAD_FAST         'self'
1735	LOAD_ATTR         'sr'
1738	LOAD_ATTR         'itemsScroll'
1741	LOAD_ATTR         'Load'
1744	LOAD_CONST        'contentList'
1747	LOAD_FAST         'scrolllist'
1750	LOAD_CONST        'headers'
1753	LOAD_FAST         'headers'
1756	CALL_FUNCTION_512 ''
1759	POP_TOP           ''
1760	JUMP_FORWARD      '1763'
1763_0	COME_FROM         '1760'
1763	LOAD_FAST         'self'
1766	RETURN_VALUE      ''
-1	RETURN_LAST       ''

Syntax error at or near `LOAD_CONST' token at offset 1134

    def RedeemSelected(self, *args):
        if self.stationID is None:
            raise UserError('RedeemOnlyInStation')
        if not len(self.selectedTokens.keys()):
            return 
        if eve.Message('RedeemConfirmClaim', {'char': self.charID,
         'station': self.stationID}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
            return 
        sm.StartService('redeem').ClaimRedeemTokens(self.selectedTokens.keys(), self.charID)
        self.Close()



    def OnTokenChange(self, checkbox, *args):
        (tokenID, massTokenID,) = checkbox.data['retval']
        k = (tokenID, massTokenID)
        gv = True
        try:
            gv = checkbox.GetValue()
        except:
            pass
        if gv:
            self.selectedTokens[k] = None
        elif k in self.selectedTokens:
            del self.selectedTokens[k]
        if len(self.selectedTokens) > 0:
            self.sr.redeemBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.redeemBtn.state = uiconst.UI_DISABLED




class RedeemToken(listentry.Item):
    __guid__ = 'listentry.RedeemToken'

    def init(self):
        self.sr.overlay = uicls.Container(name='overlay', align=uiconst.TOPLEFT, parent=self, height=1)
        self.sr.tlicon = None



    def Startup(self, *args):
        listentry.Item.Startup(self, args)
        cbox = uicls.Checkbox(text='checkbox', parent=self, configName='cb', retval=None, checked=1, align=uiconst.TOPLEFT, pos=(6, 4, 0, 0), callback=self.CheckBoxChange)
        cbox.data = {}
        self.sr.checkbox = cbox
        self.sr.checkbox.state = uiconst.UI_NORMAL



    def Load(self, args):
        listentry.Item.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetGroup(data.group)
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.checkbox.data = {'key': (data.tokenID, data.massTokenID),
         'retval': data.retval}
        self.sr.icon.left = 24
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        gdm = sm.StartService('godma').GetType(self.sr.node.info.typeID)
        if gdm.techLevel in (2, 3):
            self.sr.techIcon.left = 24
        elif self.sr.tlicon:
            self.sr.tlicon.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        lastSelected = self.sr.node.scroll.sr.lastSelected
        if lastSelected is None:
            shift = 0
        idx = self.sr.node.idx
        if self.sr.checkbox.checked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        isIt = not self.sr.checkbox.checked
        self.sr.checkbox.SetChecked(isIt)
        self.sr.node.scroll.sr.lastSelected = idx



    def GetMenu(self):
        return [(localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo, (self.sr.node,))]



    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(*args)




