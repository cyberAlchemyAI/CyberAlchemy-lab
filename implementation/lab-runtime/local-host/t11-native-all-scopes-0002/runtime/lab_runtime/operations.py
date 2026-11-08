"""Closed proposals and deterministic transaction postimages."""
from __future__ import annotations

import copy

from .common import RuntimeFault, byte_digest, digest, encoded, identity, pointer, require
from .sources import make_record, resolve, validate_histories, validate_schema
from .custody import CONTENT_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS, EXACT_SCHEMA_PROPOSAL_VERSIONS, validate_proposal_content


T11_BATCHES = {'scope:lab-integrated-model': [{'implementation:lab-candidate-catalog-generator@S02-final-candidate.0276': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': 'f5d5b1e5fd82060105c6428c4ca8a545a32d638ad44052d9ce1111a6d06b3b77'}}], 'project:cyberalchemy-v2-to-lab-migration@foundation.1': [{'implementation:lab-exact-context-generator@S02-final-candidate.0276': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': 'a04ce04cc2661e4e3dc3f99bac5d3c3f464229b1ee059db0fcb929cf8b2a6373'}}], 'protocol:lab-final-review:C10': [{'implementation:cyberalchemy-lab:repeatable-operation@S02-final-candidate.0276': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': '53fdb3188fdec44bfc44a40cbbf07557997d18f64b0c87e5876bca1f214c5213'}}], 'scope:lab-runtime-local:w06-learning-0002-560605b8': [{'implementation:lab-W06:source-adapter@candidate.1': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': '1e8e1651237da7e0172ca1f9314ad00872a0ba8a52b74100547b35b5e965c92a'}, 'implementation:lab-W06:selection-adapter@candidate.1': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': '3fd9470a82209048e56e12cb04f72ea15f01bd507ef92f1b6ca9af61f7680e87'}, 'implementation:lab-W06:application-adapter@candidate.1': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': '54cd6a78d12df3a21a68f050f387bb4d14593ef2ab50c35d1b92e59a99e84368'}, 'implementation:lab-W06:probe-adapter@candidate.1': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': '1a6315255d0d927b86c5ffddfa8d7db1ddffde2fe83d3c73ae8a61cadecc313d'}, 'implementation:lab-W06:durability-adapter@candidate.1': {'carrier': 'cal.artifact-type.implementation/v1', 'sha256': 'b336ef0af8d83f818b845dab001e037b6a8c5445fddf40a349ef97ce80f10490'}, 'operational-lesson:lab-W06:inline-role-preflight@candidate.1': {'carrier': 'cal.artifact-type.operational-lesson/v1', 'sha256': '7a3fa6a8748ed53b5c56551258f1dbf17803326e63078bd4d20e1fbf8cc80ded'}}], 'scope:lab-runtime-local:o02-source-withdrawal-fixture': [{'work:lab-O02:source-withdrawal@S02-final-candidate.0276': {'carrier': 'cal.artifact-type.work/v1', 'sha256': '79683b9ce84fe1c8dd15e729cdbc85b66490d29eb4c5bd9099cd8e7cbf6f0be7'}}], 'lab.legacy-source-assertion.cav2-product-thesis': [{'source:O05:bff6e2936d29ffcdc4bdea858b4ce4fc97f3569cccd7a030d57a6db133549a68@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '773a7bc707f1cc20bdf11aa7dc81a8d3eb09cbb40029c05b86b07ac70ad5c7b9'}, 'source:O05:abeb9e4ee611dec30dfc2d2c01153735fc1802a9ce5bae9a5faf9b4e1b43ca57@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '097650317770c9b229f25004b1f478966e797cb75c13dcefad4e063d117099ef'}, 'source:O05:4e9c15d41c7e7e4cf0f345859d68b36cc3119e5ff8dad8e97593511351e08566@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '9e8a52ee83545828ff2095914841931a25dabe9b1509b79041e8099a2f0272b6'}, 'source:O05:de2b322851e345c0d6afe1ad42ad9a5d4a7b5a866233055d65f39965acf21131@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '2f93ea2f4734255aaa6a9ffb636ce4d13b923166362bc9f41c20d9cfd477bba1'}, 'source:O05:e3aa62f4ea9ab09d7e37936ff22716c435a6406e9db31150e459ad6401413ec2@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'b52c99d1472d225b35ddafc0348d6f894640d4512d82b7d34bc802f40e6eeeb8'}, 'source:O05:7da254b4f3dcc5b262879c4d6109af2715cbbd67d6f9800d925669c989261672@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '10b78b40cf5fe86e45c4d819e85f5156aa7e0004be9b0c7cc8e3cb62903ff1a7'}, 'source:O05:c4e909ee217956e6877fcb1a3ff9d472ff35d360220785db0d3b4cee1f9144fb@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '6995e46f3e7c89835ab4f8da15414f1c236f1213776c0091643488b7580a03e5'}, 'source:O05:52d9e82403a07edb200734b92b3517395fabe43d064e79e1e4877003fe45e75f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '4c328ccb7e0b778c5e15e0a06d292aac661ec633e25efb69da0da84d96082d99'}, 'source:O05:f488c4c3ed2b66c3f7419c8e19736394019b697068d67bad4f2b13aa6cf98a3c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0c804a43fb6ce8b4e8207001945bdc650a9e9fb84c66723ce074133490ee0b2e'}, 'source:O05:af176cd00c068f7e19369b3ef46b363e07afd3df5264134d4953c30180536902@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '5b55e1381a9af39c6450e860af8bdea6febc0203b2debd2bc3cf53bef92418cc'}, 'source:O05:fefd4a3f868372dc6d83fd8b12e8ffd582197fad879b25fd263392ea69e73486@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '59a0408c7e1300b10ae29166d3fbdddd1fc28c66ba1164b097a59e2c4c795aac'}, 'source:O05:f75c1dbe81daca880c8237e1170fc8e6e08460ad0c7241b34d1ca4014346a83a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '740abaf22fbd73508467b02d2fef64f69507859eb9424d7fd850b4b16bfc18ba'}, 'source:O05:b8d6474b7cac8f1d38d2cb28ed553b546d073b8d9009468527c38fcc82cb0432@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '17ab6172fb79c64b0027310280fc5ecea3426d38d8afa7d52e1158ab9e12d9cb'}, 'source:O05:6e419179bfade655538cebc70cfe3b5f1a20c939de9c1b4b2e3842cac24150ec@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '7f229e3c96bfb10f693fd5abbee810ed75237e9a83354a4febdb08d8af0f3f76'}, 'source:O05:edc60dc33c71aea79994cc62ce9b447a4bf96757a840177254e3ce3c96e24d8b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '63b7d25a35fe8e3ce1184e21f76f7b10a9cd1dab470b2584a905f8c7b59f548f'}, 'source:O05:73ba2c46475c91512887eab3cc5426e818b4d446eb4a2ed59e07dbfc1f28603c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '218ec2a1feff7a6b41c6063e2c86a64e87ef84d22c084f5f01fc2c99b0c8d15f'}, 'source:O05:0c6d70be630c35d1f3c89b8c225482dfb8a36c78a9ba9485f260c463ac2bcdab@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '6fa9cf0de7ac56d40b9ce0569309266acab586a030675d2cf4155932ed060c55'}, 'source:O05:f63318f32b8407a2054897e9ce2da1059fc889a007f1f3f03d70616f1b5a05c5@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '032a715c579bf0191dc5cfc49a11a50bf4669c2e22a91f6a2cdbbe04e6c24d7e'}, 'source:O05:46dbe38eed5fc382d75f223a49d48bf4dd644da5186eecba73ca2cbc10889971@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'd41e0e5d5e86d23d3d6e15a344cedd703b0b00903e6c5cbe2960001d09ab07bc'}, 'source:O05:7d1c2184b572ccfdc2116369284518f8cc81eb565bddce5e2a2142e0d7d4a84d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '704a68632f70605db54eed28b3e628e3a85a8981e5a5f42e022952aa164aec79'}, 'source:O05:bb9cfc38a5998ad71022330625986f2d227184a4ff6a660ce7a542ce716974fe@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'e54b81aa7a5900f646734166a8740cf308e1b9558080769dc7620b66a9a0d28e'}, 'source:O05:d2470f7b9b75a7769cec50f355f2819e59cea7fa536e0975ceb41ff4e7b95ec0@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '8f0f10f2c8d4b74a046762001facff10d5cfe0abf713834dc4dc0f09d30619b5'}, 'source:O05:d7144c830648e9ae219a95166d02413457c7d892a32f212aebb517658da2357a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'e43836fab604b6e13f1e590cd62fa4c3a063b2ef035a10d9eefd153b8f550f1d'}, 'source:O05:dde1366c91ed2e5aa8812fbe6580238168a30e5d02508c6ee987c77f1d5fe7bd@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '19562c43d0e8d46734854a5458f31c9c8adc56b01ed90d94bc4651cc9df09b40'}, 'source:O05:e7c312fc5232bb2ee407314c4d27d25981d33b15ad88455257dff39be769884f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '69d4c8f4c28414d71f6a2373a26e860d5e34d1b59fbfa9788aaade4283ecdff2'}, 'source:O05:aa0010e6d18811c37a7cf61bedf408fd2e41e6440e171df45301e302f583698e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0a9c2b74d6fccee6ec4338563351d31a4669af7a32f65ec2f9b9acd11f2894b3'}, 'source:O05:e8709aa6700fff8bd92697da78ef3d0de0d2aee2f478d95cc98112ea8f1066bd@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'f8ba4f49818a56c432723f78dfc9d6f7c2e79f9fd0c8921422afa3502fff1581'}, 'source:O05:d21cd9ce5ac9ae934d8e8c2c99d985a6c8ba341e2616165ac72804509e7e53dc@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'b27fce6b2d858e4c4b1545f9696db598a535523ad334de469b20a8af4d0166cb'}, 'source:O05:c45700399fa07f56c6dc0c16a81f3f27c701bab9a31c248aa3452a55d861c998@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '8ac07d34ec640f750e6c793d613cfd6a65b0a314b80e5c51b2b2bd319d822129'}, 'source:O05:b60992b433b4d9c13a977fba63113af0707930eb2eac51db9bbd23d6eda0c056@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '696abecd545abe8370a634860725bb560e6872014f79e413117881776b386262'}, 'source:O05:b2ba50b8c70c509b2d9f1aee670d9f7a1ad148359f00c943614bee75104e2f8e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '771db97c178d8b3ed088f8c9520727747ce21a9828bfd5173ba87611d5fc39ee'}, 'source:O05:e453d2ac5da37b9c16e33fe6a6de6bb3f0085307e92b7cfb6cf1a5908a943aae@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1342a7f5145944aeade5d00a53b0ccadbe5d162d60d8a7b608425a2e90446fce'}, 'source:O05:72536502bad993dd382640d97b55c4cd4284cf7308815687e71a8ffd438609d4@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '5ff86b91ed84238fd346de6b72eafc2138245ab075ecce140b2be55857050797'}, 'source:O05:625396113f1e5e2799ccdf814e14d6b91435e08a45f3ee6ce4dc1d7f304192d2@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '627b85af27cb93bf544c2ed4124907f8d34ce98718ec21d0f828b6fc82bcfc00'}, 'source:O05:acf0b677522dcbb0cb88e92ad16c76258aa6245bab1f90f70679fe24b8f6e453@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'b3d52f1eb0966753b3251f23425de91be01f372decf61686408061d3f289a477'}, 'source:O05:08f6b8dfdbe5ebae63cf27344fd13b1742bebad256b7da4d10ba97b1be208b06@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '52a517335fca2ab666a5c8f1e6c95af5974946b64b5d41253cee65cdeee405e4'}, 'source:O05:c5eea3c6f2cc72c00814321bd90a368fff5c91f2d53ba6188e644ba0d562328b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '558f3591b8043d668ef0894617791ebefc670271051740fe4f8de7b62f30fee0'}, 'source:O05:f8c6c0578fd61e63dbef72b961a24c0dcf82bac2da4bcf2a0a17b0bfdf620fc0@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'd011d53f0df1a9ed321bf800c01d838c2a9b23df8362ddb866e20e8c940ab7c9'}, 'source:O05:e6bf908b52c4cf7f5b47d4d62b23e260c77f4a9962291b23b2b851ac5450d4ab@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '3420b05a02f03bc0de7177c7e86adac236f04869bdbcb2ec521acd4c1762c032'}, 'source:O05:102d1a6ddc050d42e6c0e9aa5b2bfaa66adebd88dcf02ad065e75b4b83c7b4c6@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '2bcf207e6b431298a029d6c748ccaadd87eabafb1d38c9e095b56916ecf9cb68'}, 'source:O05:997816a09d30af2c8576b0cfcb72195f35468dafd538a62cde8c1bf37eea7115@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ebc1d178dd6b3ded76b4722546d2a1ff3681ea2d92b03ec14e9aa4d617e69bc4'}, 'source:O05:1e2ac1c4ccaebfc12a99db2d0e3453f23a45e2185c7e95cc53a944f72cb3d0ff@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '383f7aefcd25c11efd34832dfb6a551e2462fcf08f3ad22aa11ca1dd58ca5ab4'}, 'source:O05:b046c559258f71b1a792be546c542a3c7dc98a0b2bae77c182f8435cb9c9f6a5@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'e4102e00f18f75f78b1b1363a4ee8483ccbd74131814ff62d21f651659aa8f8d'}, 'source:O05:6d061944ce0a83412d20c1d22039674e02356427cfe82c3ad72d4e5d9205a23a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '96bc080c267b3813f3c6c9606712e0a40b0b02068d47c2930a7efd56f7d94433'}, 'source:O05:bc87300cc20cbb70fb8baabfa3801ee9637ed9de51b26dc655666632e8f45adc@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'd9f35e52d604193e171783aa84f026cb867b3f891ab38c524bffec5754f3618e'}, 'source:O05:322de9f094255fbdb213759c071c620e1faf4aa1d2125275c23ec95c3185f0d2@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'c9138da54a9f19df55a314686b333c9793a204ed695f9eccc9ebd4421d3b5ba7'}, 'source:O05:31b8c7d92234d49251f7ddafe28cedc6701ad4a29218bbec4ff70416dfe0e3fe@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'bd62874891d6e964f31ec0115e033addb29440c3c2aa52c2221c25bf3c44831f'}, 'source:O05:fc3b03a21387c53c6ea4461b1e895e7cf52e8562f7fc81526b93ce90a8dd3723@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '044ad758054bb0afc87f7ec8009dc19d6d270c81a7bf55b1b9b755f539531d55'}, 'source:O05:021e79cda3342bd4ab0c2c5d23619fe90d2a78b863f03a78c8be0007d0de5b7b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'fa241c9e2ddd5822923b6b5868264299c73b809026cf038a8d7818c5fefe4913'}, 'source:O05:b10ac341bec8b5d2733c7c50475f6213d06680ffeb839dbdb2cc8b71a3d6dec4@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'f77cbabf8d482a04b69bacdcd33a47969169591827c895b9d31bf9714c256d97'}, 'source:O05:74d4a88d162b54bd8679a24f4087b0b8310ac9e4a832cba20db8980a1c294739@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '5d226d951604c9c3a8402a7dab0874fc6d9688b224b80b04d5cce0693702ae89'}, 'source:O05:0a660f7c5d7ceb8e019522df4af46d3517dd611aee33ef5e184ae908600f9105@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '7957023a7f12be0bf8d50b90ecf2dea02c0b882a888caba258275b1c57ac4fc0'}, 'source:O05:7d18b142eb575ec8c4e74879acf50f136c66de708c6ce0a1a7b78302073d0a16@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'c75c278a9b5ef8122145ea3ff4a144e68810979f6c6b29ef29924b7ff76054a5'}, 'source:O05:61eecd8bdf0d995683c73fe7880332b9747f6e5299e4745b44e1c345a3c67dd0@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'b302f7134fa441686d7c7fbd1e840cfd754e10ec387059db91858af835f1bb64'}, 'source:O05:08c77b5367933d7b3fbe6a1a5201096979059989f471712fb3d13276840f1dc5@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '10570b1fcb72d5262e7fe6ad609b21eee74eef9f4cbde583f56ae65bfd587ff1'}, 'source:O05:c6dca270b1362e780297a35da20ac2ed87940468e4b7e9d6be86db3f816de7ef@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '191309ff5746f699230cd1cf6cba84b5f0b66a8c669c819701fe0d25c2c4a84a'}, 'source:O05:bdd2973b42d5f504e8a45ea2db7bb087651b5842e3c80a1e2b2570ba64a59373@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1d98543595c6bdae1fc292d68af8e82540dfb86d55fd899855fa37f5b22fbf75'}, 'source:O05:f7a63750e1d2c94cc9133d1439e351976ae0be291d3c23d4c1e6893697ec98ea@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'dfe41be4499b3045498e902802b4d6c56e0384d4d4ef573897e1f0409fb4b7c3'}, 'source:O05:c29f4285dc8f6195902095a6a0985b95ee5c3a0c9c6e24c372c0bf55399ad2ea@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ed3f162e0b69d5c9cea04ca9869a762bf24cf3a71bb04eb93beeab08af4d7f87'}, 'source:O05:96acfdd4bc0a51783c6ffbae5edc29457109c392c355e8ca6bec5df0ad011a20@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1c9049028a69794ee32385b986a48dc0947a7494c443bb9fe36edd26cc9ac1bb'}, 'source:O05:54f93058ed6697d51eb809467652a323fe32b2f7476135f02cbeb930d0601e66@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '38ea876954a4b2618430eed570a57355ac24a279b072ac766bf5b8646de0a9fd'}, 'source:O05:1eae01e6882068fb580ff134be2bba1b24a120d294546b6f64948ab2f7fb3f52@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '7c1499aee32200b7474b3d73e15511f74b6b164a173dae345acde8a80c988d77'}, 'source:O05:2d099ebc900d33549db33c26e778cfaa43776a61a52ef380bd1f80a27c21c539@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '53aa3ec880be673358f4177a56d119fdb7f070db302f6aef3af97a8ebb52cb9e'}, 'source:O05:b657f93bf933423c9f75e1090c65adf0e3ec1303172b1caa0bfb143b1540dc23@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0d33a9924f9e3d50459c62c24314f000d38c511e44020c41f9fb977364009bca'}}, {'source:O05:29e9fc37b17c740a2bdb21d2b077833bcb6922a58d275995f9471da4dec7831f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '594329df814bfd0f2f86e5167a563e6d68a71803cb69680782fcfb85caf3012c'}, 'source:O05:6bdab4e613bb33a1b98af59d2ac0383256454e5c0336db5de0b529e3b5e2a5b5@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1e621b8ec141a219eb0f2343049b05d457038eb64e625b442f52f210014d595c'}, 'source:O05:67dbecb51204741bb33a5fbaabc4ed632155668220f604217df23a55f2a8c98c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ba81a33b99a4220272005cfc3e63259d70386a797521c37f05999818055b56d7'}, 'source:O05:5798fc16097a92c8313fc4c3187e10d3543bc5e1255ef826f8e328c2c2a96db9@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '35bcd43fda8d0ed7069dcb526e636f8dddc93c04ff95321403d97f27290069b7'}, 'source:O05:efa49d34703fdc7417596634acdb788c27336f985e59bc2604d51e838912fdbb@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '5a6068588d1b2f6f034b18ecde2b1300d325ce97b5a6f1b4f5849c887a16ea47'}, 'source:O05:0175751210073f3092940e9d8b5f85d82eceec22e70b88cfe524adf2e10f7c16@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '486e698794579760f53447f39fdaa5c30ee7d5b5abbea4cb52374d15edb30879'}, 'source:O05:ab6fff51694254182da898a9b92bc1624abe3cdd62f3ed616b1dd299d1dd7ac2@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0cfd01ed20f6603616e61dad01aa285d1fd7bf5573f6d10951e01549bff5b2e7'}, 'source:O05:4688bfc3892305927b630841bf7021a81deff4afce5a5ee47f85b096ff03a3c3@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '36982dfafcb3f121bb1cf154818b85becd59c1fbfa5136eb3bc105d49c4cf63a'}, 'source:O05:01b9877b235c34dd8f1f098211f5e8f4f6e3361196761f5bbc9f171d75b52d44@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'c337a2380b7735f3c0c5521dc74f701573497807ccc2da4b16e8b3663ea8596d'}, 'source:O05:f6438f5ae433463142158cb0ee7d1385407ea851395c8c7dd3ca52ec4e43391d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '9fa3ae47b64f9ed4ddf6ca8d608f5f42274c13fab463e08caa3ab7e5b1086e7d'}, 'source:O05:ce657677f00f8f54ed47b322af60e85c6c503d7ec79ded2dcf0a82f1bc20e734@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'beb036b9a846828311192e44edacca417a47e7fc32d03ca7c0001a35409c21a2'}, 'source:O05:a37d91402ff87c5e8d8f4e33d05b7362421bb4ddd20ab97e6f911e0a9fd4f34a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '95a8d660a529d225a992f16367e41f1fcd5c4390efc938c36df553d7aa49d4bd'}, 'source:O05:06b42462bbe26967ce2a5d75de274b76c4c67d44bcd4da50e8ec21c19e664eff@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'e1103b8c1923a7f0fb47e76fd49ab6af9000f535df24960ce150c8cfb6619034'}, 'source:O05:314777e0f54c91cdf689bb5f4e04f7765e522c028d66e6198384e52a0fbe7330@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'eee61bb7d592f959f2062ad56aa15b8164c7e95277be8489ea55c58bc672d831'}, 'source:O05:9555b34f86069db5653ca6c48cb07f04e0dacfc712b043d18c6852a78ecbe75d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'dc72aa2dde365dd6c72e5ca91811d177348138de754715b7f529f18efc36e898'}, 'source:O05:930b38c223244e8c3aa406179bdbdc6fb5ea32b7acb3ad24d0cc571073956823@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'b6d0360042bd3c48df6aca2ba8673a0aa7790497419ded4486740dd019db6a98'}, 'source:O05:3d9856e5f2a7778c04382b506cb98a0fd8a2b5965b40479fa0980755cce1590f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1f4de39dad106da45b422cb66c396f52ba750f555935839019d01f3bda2bf5b5'}, 'source:O05:f1b0c356e330d69226187bb03b94b6474ceea73810184086e735e0634be2fe65@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'a7ab31aa61598bfe1f0dcef9ebff9767c3e679f11e9b4d6d52f6d8358bd4b833'}, 'source:O05:cf28a78cd5a404c963c77486596e022f20a79750e2e0f1a8f83eeaa81b323f38@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0ef27b510b6be5ac4ecda4163d8c3bf2fd51608bb2b4a0639d36eb2f11377249'}, 'source:O05:b720938b1eff2b9cfecc9d863b5ac306618723097f5cd0baf94729811bdb8e2a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'd28263481cfd1fdda9979d7e99511d968ce209f8d0048ba26a17111133aef5f9'}, 'source:O05:1553cbd31a87e6e6fa5b17b258f3c62757b772c3abac25bb190a8b39bad2770e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '88e779e7244cb3615b7da6430151e0a45aeea2ee3b477f0c176648cdbde0d91d'}, 'source:O05:995f42c2a09f3aa0ea5a0d810fc67fbacbf00f4b7b53a0e4e8e39403c6fc91f8@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '80487ae5817f2e09e13907263805c8e7aed8fadd3275936c8166254e6585afbd'}, 'source:O05:5d1d7c503645bab0b2224a45c489541a19720364229305aab17d370d105770fa@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0e4f3d1e2d3a44a2eb96513ff25da4a2535291806327aa417f0e6836638970a2'}, 'source:O05:471737303ceb469856778faed918191a95c359adf5db8fbe44dd5cb6ea4b5660@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1e2f5236003d2bd43edefeb00f720a4d22181c26191b9dda46b02b1d2b6a5f6f'}, 'source:O05:9d54f15be9094f3858ed114ebeb0e2f2ddde40ea7c94a788573eb84dc80f0fdb@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '57631a5f351d8588104f3cfd302287897bdc9e99750954d32ee9c8aa84bb45dd'}, 'source:O05:f840168a4376e95da8655e4878d2c90ed0b24b5527b4433229ae5728ca53ccac@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ce48ddfe11b95398447c1f417f6994dd09d1185d774c7beb12bc132575b36a66'}, 'source:O05:c28cccd4437741317ca43d6fe80867aa9b1eee8d8bd93a5d17136d8112ac252d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1811c28d31a4152cf5616ae3ce9311da5c57659dad46c58c3bf63ab4f91bf145'}, 'source:O05:ca6bfcf5f734fbd48921f7dfe6e36b855b634db683aece97569b2bfb8480d41c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '15aefc24dcbf0049bed7e5ae0f31caddcf8caf349cc683bb9eb0e8b9e2f9ba6c'}, 'source:O05:bf966591fff4bbd3f03ba4c56df964f0df341137ae3c118654567efc4643400b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '8f4ccab602293e94d2340bc5b55588aeb688d1f48be24ea22900f380ba563d69'}, 'source:O05:5ecaa14564491cf95eec00097e3097b4f749cdfefe8915c0c16980173aa18c61@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'dcff14dd4bb91cd11071c6ea31d0776f1bf27d0f7d1e363ba04ad8ccbb7bfa28'}, 'source:O05:a5b25bb664383d9230fd2cbcc1b68352049ab8aa293f77b1ea130c2745cc4c53@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '6ddc9617843daec8f317353ffd227ae9073d406e4f2a80cd13d663f8176f680c'}, 'source:O05:2ea5237c908fc8dc6f4882402a82eafb51cbef333e496915712e5f6d8da32459@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '71c901d64c38e480d274c1a3c10b72f879f2b471a585410443fba42335882647'}, 'source:O05:2751245c38be198f9ce94e133650dbf8b000dfa329b766a473bedbeece0a6aae@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '6ee69635106c5d79ccb607ac9757c85f96533a6e2af11b39f63363fd40a483dc'}, 'source:O05:72e6d4ac2c1a066e47040da94f2b785ae3b03ee8079db5766b77dcfe5a6889ca@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'd5a96f7cf52e7fb5df67026ffeee90e291321330d511515f32033af512f34911'}, 'source:O05:ab8c09176814ca810a502b4a91a69f6e195155e8962a8c9058f073c44f5a720d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '866e3788b96efb7077b30b1d04ff1c1cb530847ace2faafbe45cf352e8f8fe04'}, 'source:O05:a947c9030dd66ebaf250b791a511a36e2bfabbb8ae56a3667555eb08d3582c1b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'b6d13cbb572df41fd73e273872ff2e83dbe57c5bed67e18f77744cfd394eec3f'}, 'source:O05:2f565baa9e81d77354339deadcb332d4537585acef8890f6642d07c56e0b5c5b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'e0c2698acb8cc50f1896419888ee9d0b3f6321326a6ab29675c5277a434415d9'}, 'source:O05:60faf6e6e53c66c1d085e6b3aa484e9cd775903b798ea90313ca816d3ec4691e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0a24a4e25e962eda895d417f4881782c4960e3134c7ebd7067b08748c0aaae71'}, 'source:O05:c20f2084395197b757f7743c3566e5a92a507bdf4428b0174a23d75506cd9f3a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '995c1effdb7df3edb8c09f6fe11f54bab8de1e0c522fc18b7e28a51d7ec2e476'}, 'source:O05:012e6196cb1a48817870b6c48a0ed4ad2b5eb12313e856d0d5c8b28a77606f6d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '8fa6291611bd801fe977c43d2e9e4a5b2f5e5ec60af50ef18d301119adfe3e97'}, 'source:O05:7b40102d21606aefba175ba467fd481fd8f7bd5062aa7b83d24bbb4612d937ef@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '2996fcd9e698ea2dc13f71b3c3ca6cacf02656360289ede7b1a38e02b264d55d'}, 'source:O05:437c505543dc8314bb67a6964f5e25542a49253721b9e2b58e5f2c11de24a0db@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '1c1717fd76847124c3e1fb20a96599922ccf4062bebaea95ff85953628207fa5'}, 'source:O05:eab332a1ff6387c746c35500e14ab8f92b68b05a6ce39c295c2c4c122cdb5a7c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'd4529201b1e5798eef814d1f578f1f4b854b12a8806d46c9be948a623b60d0f9'}, 'source:O05:427b5d55709cef32c97e21aa82d966a78e16c7272390a53285cbe105316fd6f0@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '52c976007aa51a9f54c0e0c0f49cc6ba0d073904e4ddb40fc35274787e24e0a2'}, 'source:O05:35b437d6c18506a6a5055bb771e4da44899a071d8a6f9f892d9dd516546f006f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'c84194aa993a2cb073b04a51a016924f5f801741e5f98bd5ad3c33f78f3c0c6f'}, 'source:O05:51aebc1a491fcd911aa6058a1d017b41e823f756c880237f06d2c60e6e496ed3@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '5cb8a016fcaf8bc85aca5839b7204e24ca0b1588f5bc82e19af15313dea36c07'}, 'source:O05:eefd2c08c42ae191cd5e6436ec663b4eeeed18d5aadb7766df7a8189beea1c93@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '947460c09b8ef57befc2a9dd712d0621c7646cb23b5ac316603467b54cdf5b9c'}, 'source:O05:de81cade24500d4d87a7aa6b7e84f3591cd99edf3e19076e470e1996995ba24c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '11fe25131f4e7d163ea87873229bceecebcd847736d174c38f4e2a47c20bc26a'}, 'source:O05:f793eeb71a34443f65e3ccdb7dc2034d5678323bb182d9840f2ef73b4e7a6d03@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '207e1e4ac9e882c12018bee21e73d681309f0c08d9a57691a0c31382fefdd392'}, 'source:O05:e155e5c653d073a119c25cd579840cb54bc4d04e913058431b78d4a4dbce39da@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '3434d7ba0085bcbe461df44551ed45c089854911ba701fd66e034d4f0fd636e9'}, 'source:O05:f4d18240c8172dfb0e321bf5c43e02a1ebe9dbe57d8b7b63ac6f2cff82a033aa@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ce6fdec371f28888bb23f786e55e1f30270153193ce3c7136ceb83252d40d01f'}, 'source:O05:bc13227aa1d76da181fe1f5e31cb9ddf6ad6c5d487db4e2da5d745077889f567@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ce10ef12b94aeb2ba50f76918318286c83f536acc0d8159357281a6efee152d1'}, 'source:O05:eef0e938f1ca3ae551529c3b2f6ab014d9b7d805532adc4af12b935a94506e13@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '622672ec973598aac93dbc1f2513322ee65d81f798b6f7aa70186c2059e84138'}, 'source:O05:ebc39c623727a496097bd8c721590af6b161ce2f916628baf3c518f3095bf879@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '3899f71bd5784718bb9ec889f0eb67c3dfd480bb2f9ba999b9cc19542a15cd1d'}, 'source:O05:08788b65dba30672596a2f33c95c4fe7700838af2068d12106b699a0ab2c771b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '8ce57e205416a9e1c9d783d8efb58bc7da40ec4d8b4da13c8800b2107e02c550'}, 'source:O05:e704eacd284751298bda1316e5745854042abbc875a35cd57a6ec5f8554fd7b3@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '60079aa04626deb97b411da6389f2ab59d3f1e34a7d3616bbaf147003963dacd'}, 'source:O05:755b3950b9bb78082cda805ef6f22f36edd982f408527cbcf0d1f954b4b0178c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '55f96fdce1c25a92ee5527c387606557a1e7193e7ab64ee4afae7489bb78d4c5'}, 'source:O05:179f9161ad7a329599a6865183677c8669fbe88534737baa2659b860fe99f91e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '675ca31cada8d558bb84edb1f360545592f784013adf54e54726fc8e1052f5c5'}, 'source:O05:604fa1c7e4bbd42e27ba929a9f13e744d6495fb1a4d21b4c6c2a142c068fa0de@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '300cff3e56e0e5bccedb5632d0f15b11c1f17fbce26c95ce318d4f6ff973b686'}, 'source:O05:df51e8d73f5e1e4d8791c2245b329e957159380f2009c0590cee6861666a6547@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '40384daef7a05e653e5985ab79d54365367de0eb3007d65b170065e277db934f'}, 'source:O05:e49f2447cdc0501645f6503597444f803dea77c5e577ba4db4411bda334918f5@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '0ee07fc5b5607afff1617d50414c528b1c9d12bcab2bc1627460d547b950740f'}, 'source:O05:252a2604006cab5510b6b00a45061122ca557adeb4460cc31ed24b1a9bdde62b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '4e1781a5ad6454964a1378c52ec3515fb736279d4d961aa797c304dbe318b225'}, 'source:O05:2ae3c170e24906bb302a2d38b5ada2aa7ba29c927cb7f8e15198321dc1aade17@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '53f32eee49dea27a9bfe4ca46b163d9973cbeeb43a7582cdad1b76084b88a753'}, 'source:O05:d98d86008ce911111ae7fda479c8d415879b00ee57730f1dea65136823bc20cc@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'f00fea0e6672dab4922db0b0926e0c3a79b008898577fa4f3b540db0e8b149df'}}, {'source:O05:613f76ad2d7045f9b14e72cdfe7cd9bf5544f35558bc8bb99c6ebf8e1c1286ca@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '076c8e4b88e10028933b4440181d575080d820d6d90a8ce09ef890b9c70cf780'}, 'source:O05:cc336753999b54eaf06147d564f796aceed7c94b85fa90c55735720a70364bcb@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': 'ac6f05995be7d2424549cf9345ed619edc074995ae3cd1b9927c3331466de773'}, 'source:O05:0ab55950ca1b73a9bdfa326cbbaf5f3c4e46d0205e192a59f7f818d7cad03f70@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.source/v1', 'sha256': '8a0120f029be8eb83c845c4d3102fac9680c6c50be79dcfa4dbc5d6ec6845c8e'}, 'ontology-node:4ebd4148bf6bba99eda0b3ef975384b5b30d556eee16d748d62b54a26400b83c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '12b49113fb41a1c6efb428a1a27cba1ad64993599fee1c07c0aaae587443a4ca'}, 'ontology-node:dde4282a1108d259ffeaae02dca6a57e409037d099cb6977f193da61cb32e051@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'ea362b729b5c8b9006880f96076b5dad42e640631c63d494715d5d68f839bab2'}, 'ontology-node:28c3059275c248acf6742cd064e5da4d0ccd7c3fd9853f0f6a4a69f7d3f383df@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '7b22ef4a7f36f703595a639051fb3132a9099ef2c53b1f63c75284734d6b90a0'}, 'ontology-node:e5018f40abedab91b783cef2f8dd93a5fda68562d11630983bbb7390ff719749@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'fe15d9ab27bcb1d99a5eeffb61f2870fa111b2f1f27686550b710521404cbb18'}, 'ontology-node:593014d88438271697ab945e5fabf0c382629a926f1aeb2e5468c89b5f21fa1e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '333a11675792f4593cb542ff7b34536490ee1c14e7ab1c924b7a31797b6a5c35'}, 'ontology-node:53a19648dba31c5c1b756a90ce92d27d3083e233fa81e5b7b6db5a4b73a2a8a1@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '963d362b61f703efa53921896c6b1e821c2fe1f2a5908bbaf07a28019199130b'}, 'ontology-node:080e363bcaa357681a0d7008c442b72eccc621f228e17ab0a0c2f9b9545726c7@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '6fec5cadbfa0fa37cea8095fa0d55b2ec01095e8ef7978a25db3c882e2d65aef'}, 'ontology-node:b786234a2f77246438005bedf553cb22539797f80150bd781a585f183c48dd90@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '02d8074490ca77b490dbc22932d3d16ba3040f778b327c6c926e98ad57ad56ae'}, 'ontology-node:e80126e62e04c9a73f5575b3bb026e8ddbfe78de3b3a55b8836aa4d8079067f6@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '97c4592a472e41d4b6bd0caf5bef4d9f26f28037c38d8a5f781ba77b01a82c27'}, 'ontology-node:392893c22f91d2c902981ba6a39c981991ee79e3df6e40ff019dc2e042424df4@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'e47ffead5b23d998296dfeb3ea0bdeab3f479dfdbe8b405ff5b10ca051aaeaf3'}, 'ontology-node:6823919ce065230095ef2543f526ca1f0e08229e38cea782c53fbf2d6be05d7b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '22856dbca4b0b6e0b62fe1d53c9df29895bdcafc369a124582532dc27d58da32'}, 'ontology-node:bd2c94eac33e2131c3e93b316c0adf19597a29343bcfb0785cde2f7304c05962@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '0325548833c1c360f4d9406d708b78f14829e1b7b84f128c64d8d1090b9cc356'}, 'ontology-node:f4ee88562467d4f30c51b35f35c269b3d999d7f222d1b12486d2b61524b7b435@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'dfc0487f4620801d2f0a3c394c5129efa9018388acf3b8621de7f7c91d4bbcb0'}, 'ontology-node:d05e78696929c9df5e59064582098ac9243307c5d5a9fc5c5a722035550c2d3d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '77000e8ac92d5ae2f01aa06be033899826d3491f3b1484658535cdc745ccbe67'}, 'ontology-node:30258d6f90e79dde38fb8402bb38f64c2d0243e937abc5f7e18151bbe365e204@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '652b62070fa906d7e7c69a3958ed47849581dfbb06dd81e770ee061d82a8e785'}, 'ontology-node:7d52a86e7778089a20090787529be88c95f1f481749e816484e05c1bf09f670b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '99567d18fc6c9b37a32f9e59df4ed5476b56e4de12d51201a730bd77182aa41f'}, 'ontology-node:5bd7d00b64f06841fda669b67542fca851966f1dc5c24d5f1d5fa7f2262addc0@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '9f8d9efef725ecdd8ff7d4038517bc6632834c520799153d7468b2b32821feb3'}, 'ontology-node:747788d49ed61d968dcc27245dad0c3e371b29cee8a40a480c39a789675318bf@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '70c4b63d776a98e2a940fad5cd00eb610ec5a255840815692ad3f8df5cc03f06'}, 'ontology-node:b799945957faf8e9f12586218f3313c951bd295cf040135334da17a072238aa8@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '2540f0a7075ba1992cb000d446f6796ea3869f5f939c57bb18c57d137c09b71e'}, 'ontology-node:9c689992763f87dae9a51c54f407cd5cb060290a25d35bfcf6c9f3af4cb5d8ff@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '3566bcf275f96b5ae2ded6feca9dcb6587b5e2100afbbb596b30ec75e256288a'}, 'ontology-node:e88bd6e7d898a81ae1b85eea15703b09ecd03b894cb6f1223a321a9f8c2bfbf9@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '1f4f8e48e9b028073544b2c86738335dbad38e8612f57691c7d735a14c5ef848'}, 'ontology-node:a6d741e0470e5049b65633b8ae3c6d30d0a9aeb8a5c1b29c89ec5781cb7c6e16@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '61c8d3cc83ae0fdc27ea5fee7fdd96b11731aa7b73f33fe3a49be4bf07aaac54'}, 'ontology-node:14ddc976e841fd37e62ddf74c46fa69bfe92a12210f34ed970aae19ead5040f0@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '5b150f4a37f46d84d4f52b30ca2dd03d48404fece5b7e61c860642d531ba116d'}, 'ontology-node:c52a5bf3eac37088b9106724dfae57907406cefa54d322d7c832e51eb66e4e84@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '856a7004de6195420f2ee4e748a82c824b310808d7c77e559e9ecaa2bb31ed5a'}, 'ontology-node:c84404fe9e5ad567663145fc0c7d3ce21b000b5c1e1f14cd3ae3bddd1552b102@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '73d66dd757fff5de2c6bd906a11d548f4a20066599675b331ca647bbd70bd25a'}, 'ontology-node:5699d38c8a5b9f34ebecc176dba9e3d7341334690c6f7da199863312b3b7df95@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'bbb314fb820d945874e218c43c63ed61f6777d4eb9b5358558fbb614179e6ea6'}, 'ontology-node:425866d4b07180ac2e1ec6ee08c4cd11d30a77fdfb398066e11625424a30ae48@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '3f19d549372839b316a6e3053046d4d96a350fcfc060b688b0412b145e837185'}, 'ontology-node:d5b6df63f3ff305b67a2fc18eec637276c952e683b3d3563eb013c3f5afebfaa@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'ddce18664cead077c9d07c3f33fabcf81422e6ae0d553451078fd070508e3fc8'}, 'ontology-node:fe7a5cae39fd1320be94509ae1fce2a11eeb7f34be5566ae2fef51692bb7d2b7@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '379114008cad9388da25bcb672fd2982bf593d949cd03bd56bffd6094d824c3d'}, 'ontology-node:c4828fa35aa56fd37a90e304ba0c2332f762bc8ec252b3eac6cc1ddd93a5126f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '2c67c3b36888d83116aa50efc34e5eddc0b0e8ec59b6cbe58aadb08a5435efbe'}, 'ontology-node:3d7c39e247c3ba16402938a02e435c191fd1043e283c1051558ded4e9b99e749@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '207b1249cb33f598cd5b3516981c8fe42db77fb9186036dcb6b349e1638999da'}, 'ontology-node:81d6c9f57b0f6a7b194ffdf9426ee9737263062c31e3c6e755d4d589558c27d3@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'bdf624ddfa73f0207a237b0cd9e6329041b719bcffbe9d962fae241ca8c221d7'}, 'ontology-node:f34fd30a4ed92a156b3445ebf98cda0c5713083193e173297d9e100cfb335611@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'b9f93d067ebffb5798099667bab9211f085084fcad5767b32fa5a1ef0476c65c'}, 'ontology-node:07cc1d2a69b53e5b1da276edbc19978adbb605a21e6018937aa8a840838d9449@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'b33faa43fb0925e5f4e3c42b47ea20f9a34a29a876f20991fda84dc8a8c697c8'}, 'ontology-node:cf769ba96b8a03a3fe062aa71e9b3a53115de1cf8c333de4b09398d791769cbe@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '0c70b9cddeb59352927d3d95dd162347912e766753557552341ca0afe5975016'}, 'ontology-node:2da53fd1d767e71313bd3c29de124d5021a5177f1c44ae3085de23086b414880@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': '59b88f4b12af41b183c26bafbf8164653d65c6eb091c441486653274e1ad9579'}, 'ontology-node:5e4925a722148d4ec9e01df2983bf98b8c81d1465432b12fbaafa51f3894df97@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'a1c54b99e17565f1be7e0f2d7f84d2b7e27e342ae7f8117096788317c26f6ca6'}, 'ontology-node:8cbe2bb624e64b4308ca6a258b4cf2ba62b19a8b10665b86fc94ded7e62eb53f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-node/v2', 'sha256': 'f994bbb090979f285d9746fcbb1315b6e57c3edf8f95fef930e9fc801df72554'}, 'ontology-relation:a10a2ab563cc534f1f69d35e675857976fcec93e4956e4c05682bb11d09b6a55@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '386d93f461ba1459d47bfd626243270c42b01ff760989efef4aab12ed9cb595e'}, 'ontology-relation:2d9df48693c4f44439ad4531cabab704414c424be8cbc6330ce593617961449a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '652fc481f280d2d6d4c8cde645b3860b06521a71bebacfce7e33baceb6097431'}, 'ontology-relation:258f28ecdc691f6a9506c37f1eedafc5499bc0d62e9613ef7d22d269d566edd8@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '41c41c52991055ccfc58d91d2880309093fa4b4849b997c48a925a18e34d1c12'}, 'ontology-relation:b57dc8a391c25407e356adac578a5dce745147f614d6fe385d5fd523a367ff21@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '46f9cc184a0253b3c959b0c6610860c1f42624588073b7b18b7a2a805854a8bb'}, 'ontology-relation:12670124d722529a6e1ecd4118f2e567944f81c59270861fa8364549c076d98d@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'e5223f8c510b4de96aa7fbda6ece4d7c14d1838b31368a79f14d6bac6e332cbf'}, 'ontology-relation:87abf0852b75ca76ea3b5e3f61ed344624c71c9797cb92e7fb139e545fc47bac@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'c5d965502cb30e18591d54300182c116d9d7ca47260fd89f3aab355ea473e7d5'}, 'ontology-relation:e70361795034f12fbf2bbaf41c139e8db38d4c52165a41cf4daeb9dbfae42708@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'd8145bc60d6b72ad1f38f2e0a9429fe6bccf2c3aca08adc98217fbfc38ee5240'}, 'ontology-relation:d1f557bbca5faf23423caa311a618d001d6eaaddc10d1b9e6a68e27c88ab4ec1@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'afdacb25b97a6d03eea3a7f59d1600d16309784af9f4d8014e9dfe8c1ff657ae'}, 'ontology-relation:18628ed2292baccaa3bbea4d8c8613111a831978e37722f494b44c633c3d8cd3@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'bcda24b13db49bc2dc7a292ecfdedc17fa53dc339ef363d5eb5e950c28472de6'}, 'ontology-relation:7ea9a692209a62e86c3872f9509f2642469f685237cda0ead5b42d124d94663c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'ae88f1abacb7a213074b3a9eee43f0bdd74f8a4b2df5fb1194d07d9a134784c5'}, 'ontology-relation:5a6f94f40661501098f7603f82eaa775fe482403bd340fdd8e65f713937f44d6@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'e9ce18ab9539c67c9abfc6aba717b76f0c223edfa6cb7c3ce1e55355b973e06a'}, 'ontology-relation:07acff8cd4576ee273e90f0baded87621783cd2d33cce5d31b3ce8b871e2d046@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'ac5140ce6fe93dea1f2757819103d9bffa42047277897ac3113159e115c22028'}, 'ontology-relation:36f5b2d62225d473eff6a1c943a34ee73839da9f74b0f41a48566673362b8062@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'be6247f2c01d40f1688a5f095e8769b553a93e9db0e2977bac0319c6d65647b9'}, 'ontology-relation:623c1c75723e483e092cf2447730b0eac5e09d69a7b197fe63efb4fb0c8cf6ab@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '795f2b4fe84722ca6c311d23da22a6521d90d5ee98b977a1ae5df2cb827b5b2a'}, 'ontology-relation:2f18db97edbe0f33f88c9332d4f2bb16e02dc76dff5e4f8620e431c1e954d3ae@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'ae38db92065cf6b79d54c78153303335bd0dc23568ebd3f0d69d58af11776b31'}, 'ontology-relation:fd4767a0e74d7f6e610af33b6dfc1600b010a917a88d693b2c7be5e736be444e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '6516c9211e3791a67e8b001a19b2a20082991124e29af15273fbdbd012e77258'}, 'ontology-relation:e8025d05efb07e10451ae6b5a8089b71e29b9efdfd89c7837f9f16a20d9e32a2@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'b9b54ab165cec1c33293a13371d2a70fcfe39f894da754f4de94f2af84f10d56'}, 'ontology-relation:4d96b28332f87ef18f8df7b5ee2d9a0fb6b2a8f59f20d82da777e45430a5d549@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'f895f573331aa0e7fb893f50ffdd79c1a6f02bec36e56b3af494ad1a2b885fc6'}, 'ontology-relation:afab7d54edb63fad57445b3af79ab14e153ec7d982229305160f84021a07ddc6@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '666297434a90bcf3670fe719d69d4e6b2093ea91880801dd6d4c42c298d308fc'}, 'ontology-relation:c696f01d562436723ae8b6f4b98e9c97b7c5697f9877061714d4de79c6fad2fa@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '9b0ab6296d6966748cc1eae4c1c3309433ad4a9cc735971bb9d390d30cd42da0'}, 'ontology-relation:43afccd811e6eb498d84d4cd347d1d3733ca8b4378af98026976bf7ae48e1009@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'd7074c535379e6d22c02686f4b7e9fc3abe6cafd2c77c7dec7483172b9fd217d'}, 'ontology-relation:c8e5c37c8f4ef6adff2fc0da34b0994c38056dee9b75e0a6d872c305f1d6ead8@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '34bb6d71aad70d19f5f74a1aae29ea784e3581aabf4df6f747fd6e648993fb81'}, 'ontology-relation:dd8bf5e326c3ee981da10622908e016d614dca26e95b4c5a8578ce2f98a701b6@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '52259ea3081f48b253012aa9bfb4a087002f7ebcec9be3b392a7e94a56f8515b'}}, {'ontology-relation:fdfb5f1e0e85d7047cea05a5074a1524d86903a4385335fd4071144f0b53b1da@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '4f580f4bef57fc3518a229aa8da2f1d9d983d473e542a30932e693139a6f7c7e'}, 'ontology-relation:1e54ea16a01f77454e0440c6f5683580c86eb775748c21c2be5abc53156a48aa@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '6f57752db2c8650d1775562d7ec8716e26d77485419949006c6ed8d5aea5b352'}, 'ontology-relation:91c9f49ddb93d331cf0e00a2138f5b61f0e725da8ad0ac970a705faba323875f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '854fcefb062573625a75743b9d7ef19a1f70d722574d25fff29354c2cd0866b6'}, 'ontology-relation:a40306355bfd6d48c741861237d9e3623e65bedc04aae80d46f0434dbfb403eb@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'd6981216eb9131c4d0ca31e1418742224e823a1fa4bfa761a406cbc34c8d69c0'}, 'ontology-relation:e29254eab2ca4a5865e290bfeedf17ef63577685e4556889bc6de07100ac8a7e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '14bd99f2d2bcb623c1c793f3a04913b1edef8975bebd5e39b39d2b910beb4002'}, 'ontology-relation:97f0f648a3502e5bcde19006f432f7e69049698c8b6dfe2a4490afbc0616c1e2@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'c6ee242faa19b5ae40de7b187186134b9d459db60e6e5a63f7ef87b9a9d9043c'}, 'ontology-relation:db94ecd5dcec97faa4a5d646b9ec72f62fd573babbd68d82b0d54a9cb35949c9@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '2ebc40333a87f7180e90c6af0dc4157c6b8063cacbaa77afc6be9f8a569bdecc'}, 'ontology-relation:d93befdabcc14d410e48e7715262562824fbd006d784a28c2f617d01ba17448a@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '6c81479206754a197a4578e1ef86aaa7935955a299f4f075032d911b5c8a211b'}, 'ontology-relation:3f19fa07d30431e0233daa9b2399e35786694937ff09e4ce1ed0909be75143e9@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '3e66aea1cd3f948b800811a6f5a8ef57392cc0bc68f4849b391f0db7e45b2f2b'}, 'ontology-relation:433a99f8c614fe8b171257eb5327bc0419c23723c30c5baaa08864a4a4e3bc54@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '859ad1cc8cd23f4c30b3c9e70339afb1b9b1f5a328fc47de0f2eae33f071114f'}, 'ontology-relation:3b3bf5eaf9a590f18483b3669f24fefa73a79f57df5b97c8090ce3bc93d44209@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '91f5edb8ceb7c9bdc8d0a328ea0332d0d5a4569bf2d2042ff05c32e857b688ba'}, 'ontology-relation:1e49bb919c0487ca8ed96f613570bb802f4d61a9b2577417b49c557350f94cea@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'd0b3c48f8f55f86fea625b014ecdce954038548dd15dd6ecd037c6fdb8bba9e3'}, 'ontology-relation:9330730d643028f2de8a6b53cbb05b5ca234e73f9a212a02d21c6a3ad3ce045e@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '253c27e822437c0be5381868170c179f0711f5299481621d5ae546dfa2b671ef'}, 'ontology-relation:0bb2b6140713bd36345c80b10e1bcf4ef64f4f70310622eb2fb6568b3ad5b759@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'ca066681be5e4bc40050488801cf2be8c5699b2a40a833d03cd1a1e52e8c6d67'}, 'ontology-relation:6698fea09c86e83ac52979e36a8adc3c7f44d071e8e553bf750a27f8a0fe6926@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'cf84c251c402faab0078acfdd393cc9a10bf1c7d9f5de72c62f88f6e084925fa'}, 'ontology-relation:e7ab4a94274ebe68ae2fbaefb9b59142209a1efaa0e8a73f2acc9beb04ce70a9@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '81d43aff92581ef9b62daf40a9d7392df5c6a94e74e67e94f019183048c6f9f9'}, 'ontology-relation:8e205b834c3027af6bf630e0c6670303b439d4127424cc122306eb7b9899d29f@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'dd160d2f5fc2116d61db8ff73ce4d5304afe3dcbaed3e6099bf3187aa58f02c7'}, 'ontology-relation:1762ccee7c500df7b8baedf4ea03ba7309446dc26df09dac9bcb3335992468cb@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '10e73f187a4ef22d82076834b4d3afe0c658373851454859479de8785fb7e843'}, 'ontology-relation:b742d6e866292177bcdebf8235a8c9bb4e7406369125df5e38146158aa5b0403@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '9ae73790673e1ed7bcb63bcca01eb9471471e80b06aeb47edc3ed9a1d03dae7b'}, 'ontology-relation:f3dafce78d6a262793b7a672870ad1833d85f90abb50deb3ab423caccc53a243@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '008a721e95f336325d2e3ebd389ae8eb9d1f6126dca74a628397c82c5bdf9f07'}, 'ontology-relation:653d394e3be9386ea882520cca3109cec81f8f4a8c4cd3b973a3c24a4ad2b931@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '2d346280253123b165783c44d151bf229174ce97214c0c8d7d528ed6ec7d03eb'}, 'ontology-relation:232a1f4d48eb31e1b5b231ea9dd23adc2edc1b4a9d4ffee04929070449843192@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '9cf8b78133a9835e696e67dbbfea980e402cece2903c2e789a9b247624bd5c88'}, 'ontology-relation:18a2b8d267bd2c1aa7f1bcee73385baf5c1678eb6b4e360d9a1e8b040c3e753c@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': 'a4931f4f380ab4be96c7afaea0535fd8f5e1a9555a010c8aee2c3da58a3e1aa7'}, 'ontology-relation:8fcc3f1d12ada4af215bfd781b1b874b3fa5c62d94438d0ad28691fd94daff7b@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '8a12f7bd6cd07d56e15b9b6da8d08b5d1a15eaa6f2fde3d99b2f7663d4bbde25'}, 'ontology-relation:5b433b7659c06a2b8c027c4b06a29751f02d7e920475cf551caea08555a17abc@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '9d844b790294654a348bb6e496040655aa0168225ccc404164f2c2387059bfe5'}, 'ontology-relation:bed034c4fa7fc5f8823b85b2e600253203581dd6ea1def34e70707359fedaf74@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '86755658a3b71973de73b524e418a73a9ac0ceeb22470756deefcba1cd10c985'}, 'ontology-relation:cb3ace08f58f15ecbf83d446bda6ef9a52226659d74071b638c3c01c720d6600@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.ontology-edge/v1', 'sha256': '28798576e3262efa108d555379653bd6faffcf3377260d50e67a0f621dc4a60a'}, 'generated-output:O05-selected-legacy-package@1.0.0-candidate.1': {'carrier': 'cal.artifact-type.generated-output/v2', 'sha256': 'b4bcb330e43b05d281a689d3c8d813965cde59b7cee76703d7115a8cb4298655'}}]}
T11_STORE_IDS = {'lab.legacy-source-assertion.cav2-product-thesis': 'T11-exact-scope-01', 'project:cyberalchemy-v2-to-lab-migration@foundation.1': 'T11-exact-scope-02', 'protocol:lab-final-review:C10': 'T11-exact-scope-03', 'scope:lab-integrated-model': 'T11-exact-scope-04', 'scope:lab-runtime-local:o02-source-withdrawal-fixture': 'T11-exact-scope-05', 'scope:lab-runtime-local:w06-learning-0002-560605b8': 'T11-exact-scope-06'}


def endpoint_kind(subject, projection, *, allow_historical=False):
    from .endpoint_mapping import subject_kind
    return subject_kind(subject, projection, allow_historical=allow_historical)


def endpoint_carrier_kind(carrier, projection):
    from .endpoint_mapping import carrier_kind
    return carrier_kind(carrier, projection)

CATEGORIES = ["artifact-instance", "typed-relation", "definition", "artifact-type", "relation-kind"]
OPERATIONS = ["admit", "revise", "withdraw"]
PROPOSAL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["schema_version", "proposal_id", "expected_head", "source_snapshot_digest", "scope_ref", "policy_ref", "challenge_route", "targets", "schemas"],
    "properties": {
        "schema_version": {"const": "lab-runtime-proposal/v1"},
        **{k: {"type": "string", "minLength": 1} for k in ["proposal_id", "expected_head", "source_snapshot_digest", "scope_ref", "policy_ref", "challenge_route"]},
        "schemas": {"type": "object", "additionalProperties": {"type": "object"}},
        "targets": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["category", "operation", "version_ref", "carrier_ref", "record", "predecessor_ref", "decision_ref", "contract"],
            "properties": {
                "category": {"enum": CATEGORIES}, "operation": {"enum": OPERATIONS},
                **{k: {"type": "string", "minLength": 1} for k in ["version_ref", "carrier_ref", "decision_ref"]},
                "predecessor_ref": {"type": ["string", "null"]}, "record": {"type": ["object", "null"]},
                "contract": {"type": ["object", "null"]}
            }
        }}
    }
}


LEGACY_PROPOSAL_SCHEMA=copy.deepcopy(PROPOSAL_SCHEMA)
CORRECTION_BINDING_SCHEMA={'type':'object','additionalProperties':False,'required':['path','sha256'],
    'properties':{'path':{'type':'string','minLength':1},'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}}}
CORRECTION_PROPOSAL_SCHEMA=copy.deepcopy(LEGACY_PROPOSAL_SCHEMA)
CORRECTION_PROPOSAL_SCHEMA['properties']['schema_version']={'const':'lab-runtime-proposal/v2-candidate'}
CORRECTION_PROPOSAL_SCHEMA['required'].append('correction_profile_binding')
CORRECTION_PROPOSAL_SCHEMA['properties']['correction_profile_binding']=CORRECTION_BINDING_SCHEMA
CORRECTION_TARGET_SCHEMA=CORRECTION_PROPOSAL_SCHEMA['properties']['targets']['items']
CORRECTION_TARGET_SCHEMA['required'].append('reference_correction_binding')
CORRECTION_TARGET_SCHEMA['properties']['reference_correction_binding']={'anyOf':[CORRECTION_BINDING_SCHEMA,{'type':'null'}]}
PRE_CUSTODY_PROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA]}
def with_content_schema(base, version):
    schema=copy.deepcopy(base)
    schema['properties']['schema_version']={'const':version}
    schema['required'].append('schema_contents')
    schema['properties']['schema_contents']={'type':'object','additionalProperties':CONTENT_SCHEMA}
    target=schema['properties']['targets']['items']
    target['required'].append('content')
    target['properties']['content']={'anyOf':[CONTENT_SCHEMA,{'type':'null'}]}
    return schema
ORIGINAL_PROPOSAL_SCHEMA=with_content_schema(LEGACY_PROPOSAL_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS[0])
REVIEWED_ORIGINAL_PROPOSAL_SCHEMA=with_content_schema(CORRECTION_PROPOSAL_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS[1])
EXACT_SCHEMA_ORIGINAL_PROPOSAL_SCHEMA=with_content_schema(LEGACY_PROPOSAL_SCHEMA, EXACT_SCHEMA_PROPOSAL_VERSIONS[0])
EXACT_SCHEMA_REVIEWED_PROPOSAL_SCHEMA=with_content_schema(CORRECTION_PROPOSAL_SCHEMA, EXACT_SCHEMA_PROPOSAL_VERSIONS[1])
PROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA,ORIGINAL_PROPOSAL_SCHEMA,REVIEWED_ORIGINAL_PROPOSAL_SCHEMA,EXACT_SCHEMA_ORIGINAL_PROPOSAL_SCHEMA,EXACT_SCHEMA_REVIEWED_PROPOSAL_SCHEMA]}


def protocol_check(value, schema):
    from jsonschema import Draft202012Validator
    errors = list(Draft202012Validator(schema).iter_errors(value))
    require(not errors, "protocol invalid: " + "; ".join(e.message for e in errors[:3]))


def current_contract(projection, ref):
    require(ref in projection["contracts"], f"unknown carrier: {ref}")
    contract = projection["contracts"][ref]
    require(contract["lifecycle_state"] in ("admitted-current", "local-admitted-current"), f"historical or withdrawn carrier: {ref}")
    return contract


def validate_relation(record, projection, *, allow_historical=False):
    payload = record["payload"]
    ref = payload["relation_kind_ref"]
    require(ref in projection["relation_contracts"], f"undeclared Relation Kind: {ref}")
    rc = projection["relation_contracts"][ref]["payload"]
    pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
    require(pair in rc["allowed_endpoint_pairs"], f"undeclared exact endpoint pair: {pair}")
    for endpoint in (payload["source"], payload["target"]):
        subject = resolve(projection["subjects"], endpoint["version_ref"])
        require(subject["identity"] == endpoint["ref"] and endpoint_kind(subject, projection, allow_historical=allow_historical) == endpoint["kind"], "endpoint identity/kind mismatch")
        require(subject["effective_state"] not in ("withdrawn", "local-withdrawn"), "withdrawn endpoint")
    qc = rc["qualifier_contract"]
    protocol_check(payload["qualifiers"], {"type": "object", "additionalProperties": False,
                                           "required": qc["required_axes"], "properties": qc["properties"]})


def validate_record(record, carrier, projection, *, allow_historical=False,allow_historical_carrier=False):
    if allow_historical_carrier:
        from .corrections import retained_carrier
        c=retained_carrier(projection,carrier)
    else:c=current_contract(projection,carrier)
    discriminator = c.get("instance_discriminator")
    if discriminator:
        require(pointer(record, discriminator["path"]) == discriminator["value"], "carrier discriminator mismatch")
    validate_schema(record, c["schema_path"], c.get("schema_selector"), projection["documents"])
    if record.get("kind") == "typed-relation":
        validate_relation(record, projection, allow_historical=allow_historical)
    # Source contract validation constrains any embedded global connection declarations.
    for relation in record.get("relation_refs", []):
        if not isinstance(relation, dict) or "relation_kind_ref" not in relation:
            continue
        require(relation["relation_kind_ref"] in projection["relation_contracts"], "unknown embedded Relation Kind")
        rc = projection["relation_contracts"][relation["relation_kind_ref"]]["payload"]
        own_kind = endpoint_carrier_kind(carrier, projection)
        other = relation["counterpart_kind"]
        pair = {"source_kind": own_kind, "target_kind": other} if relation["direction"] == "source" else {"source_kind": other, "target_kind": own_kind}
        require(pair in rc["allowed_endpoint_pairs"], "embedded connection has undeclared endpoint pair")


def prepare(projection, proposal, head, config, *, verify_base=True):
    protocol_check(proposal, PROPOSAL_SCHEMA)
    validate_proposal_content(proposal)
    if config['scope_ref'] in T11_BATCHES:
        # Closed <=64-member batches. Replay reaches this exact-member guard.
        batches = T11_BATCHES[config['scope_ref']]
        selected = next((batch for index, batch in enumerate(batches, 1)
                         if proposal['proposal_id'] ==
                         'T11-exact-scope-' + config['store_id'] + '-batch-' + str(index).zfill(2)), None)
        require(config['store_id'] == T11_STORE_IDS[config['scope_ref']] and
                config['owner_ref'] == 'principal:t11-local-fixture' and
                config['allowed_categories'] == ['artifact-instance'] and
                config['allowed_effects'] == ['admit'] and
                proposal['schema_version'] == ORIGINAL_PROPOSAL_VERSIONS[0] and
                proposal['schemas'] == {} and proposal['schema_contents'] == {} and
                selected is not None and
                len(proposal['targets']) == len(selected) and
                {t['version_ref'] for t in proposal['targets']} == set(selected),
                'T11 exact scope batch or fixture configuration differs')
        for t11 in proposal['targets']:
            exact = selected[t11['version_ref']]
            require(t11['category'] == 'artifact-instance' and t11['operation'] == 'admit' and
                    t11['carrier_ref'] == exact['carrier'] and
                    t11['decision_ref'] == 'decision:T11-fixture:' + byte_digest(t11['version_ref'].encode())[:16] and
                    t11['predecessor_ref'] is None and t11['contract'] is None and
                    t11['record']['node_id'] == t11['version_ref'].split('@', 1)[0] and
                    t11['record']['scope_ref'] == config['scope_ref'] and
                    t11['content']['byte_sha256'] == exact['sha256'],
                    'T11 exact member, scope or original bytes differ')
    if verify_base:
        require(proposal["expected_head"] == head, "stale expected HEAD")
    require(proposal["source_snapshot_digest"] == config["source_snapshot_digest"], "proposal source snapshot mismatch")
    require(proposal["scope_ref"] == config["scope_ref"], "proposal outside provisioned scope")
    require(proposal["policy_ref"] == config["policy_ref"] and proposal["challenge_route"] == config["challenge_route"], "policy/challenge route mismatch")
    if proposal['schema_version'] in ('lab-runtime-proposal/v2-candidate', ORIGINAL_PROPOSAL_VERSIONS[1], EXACT_SCHEMA_PROPOSAL_VERSIONS[1]):
        from .corrections import verify_config,binding
        verify_config(config,projection)
        require(proposal['correction_profile_binding']==binding(),'proposal correction profile differs')
    post = copy.deepcopy(projection)
    corrections={}
    for path, schema in proposal["schemas"].items():
        require(path.startswith("runtime/schemas/") and ".." not in path and path.endswith(".json"), "schema path outside runtime/schemas")
        require(path not in post["documents"] or post["documents"][path] == schema, "immutable schema path conflict")
        post["documents"][path] = schema
        # A schema path is a byte identity as well as a parsed value identity.
        existing=post.get('schema_content_bindings',{}).get(path)
        if proposal['schema_version'] in EXACT_SCHEMA_PROPOSAL_VERSIONS:
            entry=proposal['schema_contents'][path]
            sha=entry['byte_sha256']
            if existing:
                require(existing['byte_sha256']==sha,'immutable schema original bytes conflict')
            elif path in projection['documents']:
                require(byte_digest(encoded(projection['documents'][path]))==sha,'legacy immutable schema encoding conflict')
            else:
                post.setdefault('schema_content_bindings',{})[path]={'byte_sha256':sha,'content_ref':entry['content_ref'],
                    'encoding':'base64-original-json/v1-candidate','proposal_id':proposal['proposal_id'],
                    'selector':'/proposal/schema_contents/'+path.replace('~','~0').replace('/','~1')+'/data'}
        elif existing:
            require(byte_digest(encoded(schema))==existing['byte_sha256'],'immutable schema original bytes conflict')
    touched = set()
    identities = set()
    existing_decisions = set()
    for entry in projection["subjects"].values():
        refs = entry["decision_ref"] if isinstance(entry["decision_ref"], list) else [entry["decision_ref"]]
        existing_decisions.update(refs)
    # Stage contracts and records together, then validate against the whole proposed closure.
    for target in proposal["targets"]:
        require(target["decision_ref"] not in existing_decisions, "a recorded Decision identity cannot authorize different new effects")
        version = target["version_ref"]
        require(version not in touched, "duplicate transaction target")
        touched.add(version)
        require(target["operation"] in config["allowed_effects"] and target["category"] in config["allowed_categories"], "effect outside provisioned authority")
        prior = None
        if target["operation"] != "admit":
            require(target["predecessor_ref"] is not None, "revision/withdrawal requires exact predecessor")
            prior = resolve(post["subjects"], target["predecessor_ref"])
            require(prior["version_ref"] == target["predecessor_ref"], "predecessor must bind an exact version")
            require(prior["effective_state"] in ("admitted-current", "local-admitted-current"), "predecessor is not current")
            require(prior["category"] == target["category"], "category cannot change across revision")
        else:
            require(target["predecessor_ref"] is None, "admission cannot carry a predecessor")
        if target["operation"] == "withdraw":
            require(target["record"] is None and target["contract"] is None and version == prior["version_ref"], "withdrawal binds the existing exact revision")
            require(prior["kind"] not in ("project-state", "project-semantic-event-history", "project-governance-event-history"), "derived consequences cannot be withdrawn as user targets")
            prior["effective_state"] = "local-withdrawn"
            if target["category"] == "artifact-type":
                post["contracts"][prior["version_ref"]]["lifecycle_state"] = "local-withdrawn"
            if target["category"] == "relation-kind":
                del post["relation_contracts"][prior["identity"]]
            continue
        correction=target.get('reference_correction_binding')
        if correction is not None:
            from .corrections import validate as validate_correction
            corrections[version]=validate_correction(projection,target,proposal,config)
        record = target["record"]
        require(isinstance(record, dict), "admission requires a record")
        if "scope_ref" in record:
            require(record['scope_ref']==(corrections[version]['domain_scope_ref'] if version in corrections else proposal['scope_ref']),
                'target outside authorized scope')
        if version in corrections:
            from .corrections import retained_carrier
            carrier=retained_carrier(post,target['carrier_ref'])
        else:carrier = current_contract(post, target["carrier_ref"])
        field = carrier["artifact"].get("instance_contract", {}).get("identity_field")
        category = target["category"]
        kind = carrier["semantic_kind"]
        ident = record["artifact_type_ref"].rsplit("/", 1)[0] if category == "artifact-type" else identity(record, field)
        require(category == {"definition": "definition", "artifact-type": "artifact-type", "relation-kind": "relation-kind", "typed-relation": "typed-relation"}.get(kind, "artifact-instance"), "category/carrier semantic kind mismatch")
        if category == "artifact-type":
            require(version == record["artifact_type_ref"], "artifact contract revision identity mismatch")
        else:
            require(version.startswith(ident + "@") and len(version) > len(ident) + 1, "version must qualify exact identity")
        require(ident not in identities, "multiple targets for one identity")
        identities.add(ident)
        require(version not in post["subjects"], "immutable revision already exists")
        if prior:
            require(prior["identity"] == ident, "revision changes identity")
            prior["effective_state"] = "local-admitted-historical"
        else:
            require(not any(x["identity"] == ident and x["effective_state"] in ("admitted-current", "local-admitted-current") for x in post["subjects"].values()), "identity already current; use revise")
        require(kind not in ("project-state", "project-semantic-event-history", "project-governance-event-history", "admission-transaction"), "runtime consequences are generated, not authored targets")
        entry = {"identity": ident, "version_ref": version, "category": category, "kind": kind,
                 "effective_state": "local-admitted-current", "source": {"path": f"transactions/{proposal['proposal_id']}/{version}", "sha256": byte_digest(encoded(record))},
                 "record": record, "decision_ref": target["decision_ref"], "carrier_ref": target["carrier_ref"]}
        if proposal["schema_version"] in ORIGINAL_PROPOSAL_VERSIONS:
            entry["source"].update(sha256=target["content"]["byte_sha256"], encoding="base64-original-json/v1-candidate", content_ref=target["content"]["content_ref"])
        entry.update(identity=ident, kind=kind)
        if version in corrections:entry['reference_correction_proof']=copy.deepcopy(corrections[version])
        post["subjects"][version] = entry
        if category == "artifact-type":
            c = target["contract"]
            require(isinstance(c, dict), "new artifact type requires exact schema binding")
            required = {"semantic_kind", "schema_path", "schema_sha256", "schema_selector", "instance_discriminator", "identity_field", "allowed_relation_kinds", "relation_roles"}
            require(set(c) == required, "artifact contract binding must be closed")
            from .protocols import CONTRACT_BINDING_SCHEMA
            protocol_check(c, CONTRACT_BINDING_SCHEMA)
            require(c["schema_path"] in post["documents"], "artifact type schema not in proposed closure")
            original_binding=post.get('schema_content_bindings',{}).get(c['schema_path'])
            if original_binding:
                expected_schema_sha=original_binding['byte_sha256']
            elif proposal['schema_version'] in EXACT_SCHEMA_PROPOSAL_VERSIONS:
                known={x['schema_sha256'] for x in projection['contracts'].values() if x['schema_path']==c['schema_path']}
                require(len(known)<=1,'ambiguous captured original schema identity')
                expected_schema_sha=next(iter(known)) if known else byte_digest(encoded(post['documents'][c['schema_path']]))
            else:
                expected_schema_sha=byte_digest(encoded(post['documents'][c['schema_path']]))
            require(c['schema_sha256']==expected_schema_sha,'artifact schema digest mismatch')
            require(all(record[k] == c[k] for k in ("semantic_kind", "schema_path", "schema_sha256", "schema_selector")), "descriptor differs from schema package binding")
            require(isinstance(c["identity_field"], str) and c["identity_field"], "explicit instance identity field required")
            require(isinstance(c["allowed_relation_kinds"], list) and isinstance(c["relation_roles"], list), "closed endpoint declaration lists required")
            artifact = {**record, "instance_contract": {"identity_field": c["identity_field"], "instance_discriminator": c["instance_discriminator"]},
                        "allowed_relation_kinds": c["allowed_relation_kinds"], "relation_roles": c["relation_roles"]}
            post["contracts"][version] = {**c, "artifact_type_ref": version, "artifact": artifact, "lifecycle_state": "local-admitted-current"}
            if prior:
                post["contracts"][prior["version_ref"]]["lifecycle_state"] = "local-admitted-historical"
        else:
            require(target["contract"] is None, "schema contract binding only belongs to artifact-type targets")
        if category == "relation-kind":
            require(record["payload"]["relation_kind_id"] == ident, "Relation Kind identity mismatch")
            post["relation_contracts"][ident] = record
    # Check touched records and extension closure after all staging.
    for target in proposal["targets"]:
        if target["operation"] == "withdraw":
            continue
        if target["category"] == "artifact-type":
            require(target["carrier_ref"] == "cal.artifact-type.artifact-type/v3", "type registration requires the declared v3 descriptor slot")
            meta = current_contract(post, target["carrier_ref"])
            validate_schema(target["record"], meta["schema_path"], "#/properties/registered_types/items", post["documents"])
            refs = target["record"]["semantic_definition_refs"]
            require(all(ref in post["subjects"] for ref in refs), "artifact type has an unresolved Definition binding")
        else:
            validate_record(target["record"], target["carrier_ref"], post, allow_historical=target["version_ref"] in corrections,allow_historical_carrier=target["version_ref"] in corrections)
        if target["category"] == "relation-kind":
            record = target["record"]
            for ref, other in projection["relation_contracts"].items():
                if ref != record["node_id"]:
                    require(other["payload"]["axis_id"] != record["payload"]["axis_id"], "new Relation Kind collapses an existing typed axis")
            current_kinds = {endpoint_carrier_kind(ref, post) for ref, c in post["contracts"].items() if c["lifecycle_state"] in ("admitted-current", "local-admitted-current")}
            prior_pairs = projection["relation_contracts"].get(record["node_id"], {}).get("payload", {}).get("allowed_endpoint_pairs", [])
            for pair in record["payload"]["allowed_endpoint_pairs"]:
                require(pair["source_kind"] in current_kinds and pair["target_kind"] in current_kinds, "Relation Kind endpoint has no current carrier")
                if pair in prior_pairs:
                    continue
                # Every affected carrier must permit this relation explicitly.
                for direction, kind, counterpart in (("source", pair["source_kind"], pair["target_kind"]), ("target", pair["target_kind"], pair["source_kind"])):
                    cs = [c for ref, c in post["contracts"].items() if c["lifecycle_state"] in ("admitted-current", "local-admitted-current") and endpoint_carrier_kind(ref, post) == kind]
                    require(any(record["node_id"] in c["artifact"].get("allowed_relation_kinds", []) for c in cs), "Relation Kind extension requires explicit endpoint carrier successor")
                    require(any(any(role.get("relation_kind_ref") == record["node_id"] and role.get("direction") == direction and counterpart in role.get("counterpart_kinds", []) for role in c["artifact"].get("relation_roles", [])) for c in cs), "Relation Kind extension requires exact directional endpoint role declarations")
    # New withdrawals/revisions must not invalidate existing active local relations.
    for entry in post["subjects"].values():
        if entry["category"] == "typed-relation" and entry["effective_state"] in ("admitted-current", "local-admitted-current"):
            old = projection["subjects"].get(entry["version_ref"])
            if old:
                try:
                    validate_relation(old["record"], projection, allow_historical=True)
                except RuntimeFault:
                    # Existing exact-version residue remains a diagnostic; it grants no new connection.
                    continue
            validate_relation(entry["record"], post, allow_historical=old is not None or entry["version_ref"] in corrections)
        if entry["category"] == "artifact-type" and entry["effective_state"] in ("admitted-current", "local-admitted-current"):
            for ref in entry["record"].get("semantic_definition_refs", []):
                if ref in post["subjects"]:
                    require(post["subjects"][ref]["effective_state"] != "local-withdrawn", "active carrier depends on withdrawn Definition")
    cores = [{"decision_ref": t["decision_ref"], "category": t["category"], "operation": t["operation"],
              "version_ref": t["version_ref"], "target_digest": digest(t)} for t in proposal["targets"]]
    for core in cores:
        if core['version_ref'] in corrections:core.update(copy.deepcopy(corrections[core['version_ref']]))
    require(len({c["decision_ref"] for c in cores}) == len(cores), "each independent target requires an independent stable Decision core")
    return post, cores


def consequences(projection, proposal, cores, approval, sequence, store_id):
    from .governance import records as governance_records
    old_state = projection["state"]
    state = copy.deepcopy(old_state)
    history = copy.deepcopy(projection["histories"])
    decision_refs = [c["decision_ref"] for c in cores]
    tx_path = f"transactions/{sequence:010d}.json"
    for i, target in enumerate(proposal["targets"]):
        if target["operation"] != "withdraw":
            binding = projection["subjects"][target["version_ref"]]["source"]
            binding.update(path=tx_path, selector=f"/proposal/targets/{i}/record", store_id=store_id)
            if proposal["schema_version"] in ORIGINAL_PROPOSAL_VERSIONS:
                binding.update(selector=f"/proposal/targets/{i}/content/data", record_selector=f"/proposal/targets/{i}/record")
    for binding in projection.get('schema_content_bindings',{}).values():
        if binding['proposal_id']==proposal['proposal_id']:
            binding.update(path=tx_path,store_id=store_id)
    tx_ref = f"admission-transaction:{store_id}:{sequence}"
    state_ref = f"project-state:{store_id}:{sequence}"
    record_ref = f"runtime-transaction:{store_id}:{sequence}"
    state["node_id"] = state_ref
    state["scope_ref"] = proposal["scope_ref"]
    state["name"] = f"Local Project State {store_id} transaction {sequence}"
    state["evidence_refs"] = [record_ref]
    state["claim_ceiling"] = "Local operational successor over a frozen admitted baseline; no repository admission, deployment or external activation."
    state["relation_refs"] = [{"counterpart_kind": "project", "counterpart_ref": proposal.get("project_ref", old_state["payload"]["project_ref"]), "direction": "source", "relation_kind_ref": "relation.member-of"},
                              {"counterpart_kind": "project-state", "counterpart_ref": old_state["node_id"], "direction": "source", "relation_kind_ref": "relation.successor-of"},
                              {"counterpart_kind": "admission-transaction", "counterpart_ref": tx_ref, "direction": "target", "relation_kind_ref": "relation.materializes-consequence"}]
    p = state["payload"]
    p["cursor"] = record_ref
    p["decision_refs"] = old_state["payload"]["decision_refs"] + decision_refs
    p["artifact_refs"] = list(dict.fromkeys(old_state["payload"]["artifact_refs"] + [t["version_ref"] for t in proposal["targets"]] + [record_ref]))
    p["state_digest"] = "sha256:" + digest({"predecessor": old_state["payload"]["state_digest"], "proposal": digest(proposal), "decisions": cores})
    semantic_history = history["project-semantic-event-history"]["payload"]
    gov_history = history["project-governance-event-history"]["payload"]
    cursor = len(semantic_history["events"]) + 1
    semantic = {"event_id": f"project-semantic-event:{store_id}:{sequence}", "cursor": cursor,
                "previous_event_digest": semantic_history["events"][-1]["event_digest"], "change_kind": "local-admission-transaction",
                "predecessor_state_ref": old_state["node_id"], "predecessor_state_digest": old_state["payload"]["state_digest"],
                "resulting_state_ref": state_ref, "resulting_state_digest": p["state_digest"],
                "material_refs": [{"path": t["version_ref"], "sha256": digest(t)} for t in proposal["targets"]],
                "record_ref": record_ref, "semantic_summary": "Applied exact local targets and deterministic Project State consequences."}
    semantic["event_digest"] = digest(semantic)
    gov = {"event_id": f"project-governance-event:{store_id}:{sequence}", "governance_cursor": len(gov_history["events"]) + 1,
           "previous_event_digest": gov_history["events"][-1]["event_digest"],
           "semantic_event_ref": {"semantic_event_id": semantic["event_id"], "semantic_event_digest": semantic["event_digest"], "semantic_cursor": cursor},
           "decision_ref": "decision-bundle:" + digest(cores), "authorization_ref": "runtime-approval:" + digest(approval),
           "authorization_sha256": byte_digest(encoded(approval)), "policy_ref": proposal["policy_ref"],
           "challenge_contract_ref": proposal["challenge_route"], "upstream_governance_evidence_refs": decision_refs,
           "record_ref": record_ref, "governance_summary": "Verified provisioned local owner signature for exact scope, base HEAD and targets."}
    gov["event_digest"] = digest(gov)
    for key, event, watermark in [("project-semantic-event-history", semantic, "latest_cursor"), ("project-governance-event-history", gov, "latest_governance_cursor")]:
        h = history[key]
        h["payload"]["events"].append(event)
        h["payload"][watermark] += 1
        h["payload"]["chain_digest"] = digest([e["event_digest"] for e in h["payload"]["events"]])
        h["evidence_refs"] = [record_ref]
        h["scope_ref"] = proposal["scope_ref"]
        h["claim_ceiling"] = state["claim_ceiling"]
    receipt_ref = "runtime-receipt:" + record_ref
    governance = governance_records(projection, proposal, cores, approval, store_id, sequence)
    transaction = copy.deepcopy(projection["documents"]["authority/admissions/governance-transaction-surface/v1/instances/governance/admission-transaction.json"])
    transaction.update(node_id=tx_ref, name="Local authorized Admission Transaction", scope_ref=proposal["scope_ref"],
                       evidence_refs=[gov["authorization_ref"]], claim_ceiling=state["claim_ceiling"], relation_refs=[{
                           "counterpart_kind": "policy", "counterpart_ref": proposal["policy_ref"], "direction": "source", "relation_kind_ref": "relation.governed-by"}])
    registries = {"coverage": "authored-targets-and-pre-consequence-subjects", "subjects": {k: {x: v[x] for x in ("identity", "version_ref", "category", "kind", "effective_state", "source", "decision_ref")} for k, v in projection["subjects"].items()},
                  "contracts": projection["contracts"], "relation_contracts": projection["relation_contracts"]}
    generated = copy.deepcopy(projection["documents"]["authority/admissions/governance-transaction-surface/v1/instances/generated-output.json"])
    generated.update(node_id=f"generated-output:{store_id}:{sequence}", name="Local registry and index projection", scope_ref=proposal["scope_ref"],
                     evidence_refs=[record_ref], claim_ceiling=state["claim_ceiling"] + " This output indexes authored targets and pre-consequence subjects; the complete current catalog is replay-derived.")
    generated["relation_refs"][0]["counterpart_ref"] = tx_ref
    generated["payload"].update(generator_ref="implementation:lab-operational-runtime/v1", input_refs=[t["version_ref"] for t in proposal["targets"]],
                                output_digest="sha256:" + digest(registries), reproducibility_receipt_ref=receipt_ref)
    transaction["payload"].update(
        decision_bundle_ref=gov["decision_ref"], resolved_bundle_digest=digest(cores), review_bundle_digest=digest(proposal),
        decision_core_refs=[{"decision_ref": c["decision_ref"], "decision_core_sha256": digest(c), "selected_outcome": c["operation"]} for c in cores],
        authorization_evidence_ref=gov["authorization_ref"], authorization_evidence_sha256=gov["authorization_sha256"],
        admission_targets=[{"target_ref": t["version_ref"], "target_sha256": digest(t), "effect_kind": t["operation"]} for t in proposal["targets"]],
        input_state_ref=old_state["node_id"], input_state_sha256=byte_digest(encoded(old_state)), project_ref=p["project_ref"],
        deterministic_consequences=[{"consequence_kind": x["kind"], "consequence_ref": x["node_id"], "output_sha256": byte_digest(encoded(x)), "declared_input_ref": gov["decision_ref"]} for x in [state, *history.values(), generated]],
        application_receipt_ref=receipt_ref, rollback_ref="runtime-recovery:committed-head", runtime_activations=0, external_effect_refs=[])
    for record in [state, *history.values(), generated, transaction, *governance]:
        cs = [ref for ref, c in projection["contracts"].items() if c["semantic_kind"] == record["kind"] and c["lifecycle_state"] in ("admitted-current", "local-admitted-current")]
        require(len(cs) == 1, "ambiguous consequence carrier")
        validate_record(record, cs[0], projection)
        for prior in projection["subjects"].values():
            if prior["kind"] == record["kind"] and record["kind"] in ("project-state", "project-semantic-event-history", "project-governance-event-history") and prior["effective_state"] in ("admitted-current", "local-admitted-current"):
                prior["effective_state"] = "local-admitted-historical"
        ver = record["node_id"] + "@local." + str(sequence)
        projection["subjects"][ver] = make_record(record, category="artifact-instance", version=ver, state="local-admitted-current",
                                                  path=record_ref, sha=byte_digest(encoded(record)), decision=decision_refs, carrier=cs[0])
        if record is state:
            selector = "/consequences/project_state"
        elif record in history.values():
            selector = "/consequences/histories/" + record["kind"]
        elif record is generated:
            selector = "/consequences/generated_output"
        elif record is transaction:
            selector = "/consequences/admission_transaction"
        else:
            selector = "/consequences/governance_records/" + str(governance.index(record))
        projection["subjects"][ver]["source"].update(path=tx_path, selector=selector, store_id=store_id)
    projection["state"] = state
    projection["histories"] = history
    # These six fixed, declared deterministic connections are covered by the signed
    # protocol/source snapshot. They are instances of existing axes, not new meanings.
    typed_carriers = [ref for ref, c in projection["contracts"].items() if c["semantic_kind"] == "typed-relation" and c["lifecycle_state"] in ("admitted-current", "local-admitted-current")]
    require(len(typed_carriers) == 1, "ambiguous current Typed Relation consequence carrier")
    typed_carrier = typed_carriers[0]
    def endpoint(record):
        entry = resolve(projection["subjects"], record["node_id"])
        return {"kind": endpoint_kind(entry, projection), "ref": entry["identity"], "version_ref": entry["version_ref"]}
    project = resolve(projection["subjects"], state["payload"]["project_ref"])
    connections = [(state, old_state, "relation.successor-of", {"succession_effect": "continues-and-supersedes-current-state"}),
                   (state, project["record"], "relation.member-of", {"membership_role": "durable-project-state"})]
    for result in [state, *history.values(), generated]:
        connections.append((transaction, result, "relation.materializes-consequence", {"consequence_role": result["kind"],
                            "output_digest": "sha256:" + byte_digest(encoded(result)), "application_receipt_ref": receipt_ref}))
    relation_records = []
    for i, (source, target, predicate, qualifiers) in enumerate(connections):
        relation = copy.deepcopy(projection["documents"]["authority/admissions/governance-transaction-surface/v1/instances/typed-relations/materializes-project-state.json"])
        source_ep = endpoint(source)
        if target is old_state:
            old = next(v for v in projection["subjects"].values() if v["kind"] == "project-state" and v["record"]["node_id"] == old_state["node_id"])
            target_ep = {"kind": old["kind"], "ref": old["identity"], "version_ref": old["version_ref"]}
        elif target is project["record"]:
            target_ep = {"kind": endpoint_kind(project, projection), "ref": project["identity"], "version_ref": project["version_ref"]}
        else:
            target_ep = endpoint(target)
        relation.update(node_id=f"typed-relation:{store_id}:{sequence}:{i}", name="Deterministic local " + predicate,
                        schema_version=projection["contracts"][typed_carrier]["instance_discriminator"]["value"],
                        lifecycle_state="active", scope_ref=proposal["scope_ref"], evidence_refs=[record_ref], claim_ceiling=state["claim_ceiling"])
        relation["payload"].update(relation_kind_ref=predicate, source=source_ep, target=target_ep, qualifiers=qualifiers,
                                    relation_lifecycle_state="active", relation_evidence_refs=[record_ref])
        validate_record(relation, typed_carrier, projection)
        version = relation["node_id"] + "@local." + str(sequence)
        entry = make_record(relation, category="typed-relation", version=version, state="local-admitted-current", path=tx_path,
                            sha=byte_digest(encoded(relation)), decision=decision_refs, carrier=typed_carrier)
        entry["source"].update(selector="/consequences/typed_relations/" + str(i), store_id=store_id)
        projection["subjects"][version] = entry
        relation_records.append(relation)
    validate_histories(history)
    receipt = {"schema_version": "lab-runtime-application-receipt/v1", "transaction_ref": tx_ref, "proposal_digest": digest(proposal),
               "authorization_digest": digest(approval), "decision_core_digests": [digest(c) for c in cores],
               "outputs": [{"kind": x["kind"], "identity_ref": x["node_id"], "sha256": byte_digest(encoded(x))} for x in [state, *history.values(), generated, transaction, *governance, *relation_records]],
               "semantic_cursor": cursor, "governance_cursor": gov["governance_cursor"], "application_state": "applied",
               "authority_boundary": "provisioned-local-store", "repository_admission_effect": "none", "runtime_activations": 0, "external_effects": 0}
    return {"project_state": state, "histories": history, "admission_transaction": transaction, "generated_output": generated,
            "registry_projection": registries, "governance_records": governance, "typed_relations": relation_records, "receipt": receipt}
